# UTS II3160 Teknologi Sistem Terintegrasi
Afif Fahreza / 18219058

Deployment Link: [https://uts-tst-afif.herokuapp.com](https://uts-tst-afif.herokuapp.com)
## Endpoints
**GET**
- / : root, return nama nim
- /docs : dokumentasi API
- /menu : read semua menu
- /menu/{item_id} : read menu dengan item_id yang dipilih
- /users/me : read user me

**POST**
- /menu : create menu, request body nama dari menu karena id auto increment
- /token : login untuk mendapatkan token
- /register : register (create user), request body username, password, email, name

**PUT**
- /menu/{item_id} : update menu dengan item_id yang dipilih, request body id dan nama baru

**DELETE**
- /menu/{item_id} : delete menu dengan item_id yang dipilih

## Known Bugs
Pada API yang telah dideploy, setiap ada create/update terhadap file JSON, write file sepertinya terbuat baru sehingga kadang-kadang hasil read berbeda dan seolah-olah tidak berhasil dilakukan create/update. Masalah ini tidak terjadi jika run di local.

## How to run locally
Pastikan python 3 sudah terinstall.
```bash
git clone https://github.com/afiffahreza/uts-tst-api.git
cd uts-tst-api
pip install -r requirements.txt
uvicorn api:app --reload
```
