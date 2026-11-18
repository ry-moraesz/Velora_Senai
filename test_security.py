from app.security import hash_password,verify_password,token_for,decode_token
def test_password_hash_roundtrip():
 hashed=hash_password('Correct-Horse-Battery-42!'); assert hashed!='Correct-Horse-Battery-42!'; assert verify_password('Correct-Horse-Battery-42!',hashed); assert not verify_password('wrong',hashed)
def test_jwt_claims():
 data=decode_token(token_for(7,3,'ADMIN')); assert data['sub']=='7' and data['company']==3
