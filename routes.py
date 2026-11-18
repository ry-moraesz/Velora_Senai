import secrets,io
from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.models import *
from app.schemas import *
from app.security import hash_password,verify_password,token_for
from app.deps import current_user,roles
router=APIRouter(prefix='/api/v1')
@router.post('/auth/bootstrap')
def bootstrap(data:Bootstrap,db:Session=Depends(get_db)):
 if db.scalar(select(func.count(User.id))): raise HTTPException(403,'Bootstrap já utilizado')
 c=Company(name=data.company_name,cnpj=data.cnpj); db.add(c); db.flush(); u=User(company_id=c.id,name=data.name,email=data.email.lower(),password_hash=hash_password(data.password),role='ADMIN'); db.add(u); db.commit(); return {'created':True}
@router.post('/auth/login')
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
 users=db.scalars(select(User).where(User.email==form.username.lower(),User.active.is_(True))).all(); u=next((x for x in users if verify_password(form.password,x.password_hash)),None)
 if not u: raise HTTPException(401,'Credenciais inválidas')
 return {'access_token':token_for(u.id,u.company_id,u.role),'token_type':'bearer','user':{'name':u.name,'email':u.email,'role':u.role,'company_id':u.company_id}}
@router.get('/auth/me')
def me(u:User=Depends(current_user),db:Session=Depends(get_db)): return {'id':u.id,'name':u.name,'email':u.email,'role':u.role,'company_id':u.company_id,'company':db.get(Company,u.company_id).name}
@router.get('/dashboard')
def dashboard(u:User=Depends(current_user),db:Session=Depends(get_db)):
 rows=db.execute(select(Asset.state,func.count()).where(Asset.company_id==u.company_id).group_by(Asset.state)).all(); recent=db.scalars(select(Movement).where(Movement.company_id==u.company_id).order_by(Movement.created_at.desc()).limit(8)).all()
 return {'totals':{s:n for s,n in rows},'assets_total':sum(n for _,n in rows),'recent_movements':[{'id':m.id,'asset_id':m.asset_id,'type':m.type,'created_at':m.created_at,'purpose':m.purpose} for m in recent]}
@router.get('/assets')
def list_assets(search:str|None=None,db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=select(Asset).where(Asset.company_id==u.company_id)
 if search:q=q.where(Asset.name.ilike(f'%{search}%')|Asset.code.ilike(f'%{search}%'))
 return [{'id':a.id,'code':a.code,'name':a.name,'category':a.category.name,'serial_number':a.serial_number,'block':a.block.name,'sector':a.block.sector.name,'state':a.state,'responsible_id':a.responsible_id} for a in db.scalars(q.order_by(Asset.id.desc()).limit(250)).all()]
@router.post('/assets')
def create_asset(data:AssetCreate,db:Session=Depends(get_db),u:User=Depends(roles('ADMIN','MANAGER'))):
 cat=db.get(Category,data.category_id); block=db.get(Block,data.block_id)
 if not cat or cat.company_id!=u.company_id or not block or block.sector.company_id!=u.company_id: raise HTTPException(400,'Categoria ou bloco inválido')
 if block.sector.categories and cat not in block.sector.categories: raise HTTPException(422,'Categoria incompatível com setor')
 count=db.scalar(select(func.count(Asset.id)).where(Asset.company_id==u.company_id,Asset.category_id==cat.id)); a=Asset(company_id=u.company_id,category_id=cat.id,block_id=block.id,responsible_id=data.responsible_id,code=f'{cat.prefix.upper()}#{count+1:03d}',name=data.name,description=data.description,serial_number=data.serial_number,acquired_on=data.acquired_on,value=data.value,state=data.state,qr_token=secrets.token_urlsafe(24)); db.add(a); db.flush(); db.add(AuditLog(company_id=u.company_id,user_id=u.id,action='CREATE',table_name='assets',record_id=str(a.id))); db.commit(); return {'id':a.id,'code':a.code,'qr_token':a.qr_token}
@router.get('/assets/{asset_id}')
def asset_detail(asset_id:int,db:Session=Depends(get_db),u:User=Depends(current_user)):
 a=db.scalar(select(Asset).where(Asset.id==asset_id,Asset.company_id==u.company_id))
 if not a: raise HTTPException(404,'Ativo não encontrado')
 moves=db.scalars(select(Movement).where(Movement.asset_id==a.id,Movement.company_id==u.company_id).order_by(Movement.created_at.desc())).all()
 return {'id':a.id,'code':a.code,'name':a.name,'description':a.description,'serial_number':a.serial_number,'category':a.category.name,'block':a.block.name,'sector':a.block.sector.name,'state':a.state,'qr_token':a.qr_token,'movements':[{'type':m.type,'from':m.origin_block_id,'to':m.destination_block_id,'created_at':m.created_at,'purpose':m.purpose,'returned_at':m.returned_at} for m in moves]}
@router.get('/assets/{asset_id}/qr')
def qr(asset_id:int,db:Session=Depends(get_db),u:User=Depends(current_user)):
 import qrcode
 a=db.scalar(select(Asset).where(Asset.id==asset_id,Asset.company_id==u.company_id))
 if not a:raise HTTPException(404,'Ativo não encontrado')
 image=qrcode.make(f'velora://asset/{a.qr_token}'); buf=io.BytesIO(); image.save(buf,format='PNG'); buf.seek(0); return StreamingResponse(buf,media_type='image/png')
@router.post('/assets/{asset_id}/movements')
def move(asset_id:int,data:MoveCreate,db:Session=Depends(get_db),u:User=Depends(current_user)):
 try:
  a=db.scalar(select(Asset).where(Asset.id==asset_id,Asset.company_id==u.company_id).with_for_update())
  dest=db.get(Block,data.destination_block_id)
  if not a or not dest or dest.sector.company_id!=u.company_id:raise HTTPException(404,'Ativo ou destino não encontrado')
  if a.state in ['LOST','RETIRED']:raise HTTPException(409,'Ativo extraviado/baixado não pode ser movimentado')
  if data.type=='WITHDRAWAL' and a.state!='AVAILABLE':raise HTTPException(409,'Somente ativo disponível pode ser retirado')
  if data.type not in ['WITHDRAWAL','RETURN','TRANSFER']:raise HTTPException(422,'Tipo inválido')
  origin=a.block_id; m=Movement(company_id=u.company_id,asset_id=a.id,user_id=u.id,origin_block_id=origin,destination_block_id=dest.id,type=data.type,purpose=data.purpose,due_at=data.due_at); a.block_id=dest.id
  if data.type=='WITHDRAWAL':a.state='IN_USE'
  if data.type=='RETURN':
   a.state='AVAILABLE'; prev=db.scalar(select(Movement).where(Movement.asset_id==a.id,Movement.type=='WITHDRAWAL',Movement.returned_at.is_(None)).order_by(Movement.created_at.desc()).with_for_update())
   if prev:prev.returned_at=func.now()
  db.add(m); db.flush(); db.add(AuditLog(company_id=u.company_id,user_id=u.id,action='MOVEMENT_'+data.type,table_name='movements',record_id=str(m.id))); db.commit(); return {'id':m.id,'asset_id':a.id,'location_block_id':a.block_id,'state':a.state}
 except Exception:db.rollback();raise
