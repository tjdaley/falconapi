from pymongo import MongoClient

# Connect to the MongoDB client
client = MongoClient("mongodb://ec2-54-235-51-13.compute-1.amazonaws.com:27017/")
db = client["falcon"]
extendedprops_collection = db["extendedprops"]

MY_LIST=[
  "c8aa77d2-1443-4db1-915b-917112a0d239",
  "ed7241fe-1340-4191-be95-1d63757a22a9",
  "ce4fb372-a5f0-445a-a5aa-c866ae14306b",
  "9ba400fe-2670-4406-b51d-d4e1f09b8f25",
  "150561c8-ca15-4290-a14c-3adf479c3d89",
  "43c9f87e-3ea7-4a8d-a36a-c14ff41ce1eb",
  "6c649b76-f77d-4125-971b-25a0e24c1afc",
  "67fdf277-ecba-454a-b636-c39709f8ae3e",
  "8f76b02a-c21c-417a-b16e-c6753eac90af",
  "7dfc56fe-ae1c-4e19-aa23-8550bbc430ac",
  "25c5acce-ec80-4592-a6ea-a907229e49ff",
  "1313d926-835b-48b5-b384-8650208a9323",
  "2fc35f28-9d97-423f-886e-c004194ce980",
  "3ef383df-f37c-4897-ae37-7a60a4e1c682",
  "31d445d2-b497-45d7-b309-62a4158627fe",
  "8e02e09e-a5fc-44ce-a7b6-e2f913a8c364",
  "7d0c0a3c-5db8-449b-81ca-546247c0f17d",
  "f5d05335-0e64-4dad-a8d9-4ad1aa606412",
  "5f701644-af40-4c29-91eb-87ad68dedf83",
  "e54d9585-58fd-4edf-a3b6-66bbfb1f481e",
  "d2a142ad-745d-4705-9990-2dcdd501aa25",
  "4145afb1-787e-4a42-93bc-2fa0a835c6d8",
  "6f728fe2-918a-47ae-b43a-96748bba1cc1",
  "091323d0-2f58-438c-8217-17386e2fc572",
  "ce71184c-6a31-4c01-8fdb-51e64c1e7ac0",
  "0ce5bada-664f-47da-91d8-6d17815b83c2",
  "d9dc36bc-fb42-435e-8e1f-943fb4f8ace8",
  "ed9eb3e1-84a3-42e8-8021-b8505972752e",
  "d40a4e6b-66ac-4f4c-aa8a-13e968dbab66",
  "f758426f-6449-4766-b3a2-aa620ecb7d29",
  "190e9eb5-363a-4495-8804-50e905c53ead",
  "4477c14e-c159-4ab1-b1fc-369bac813aeb",
  "0c0c4c9e-5557-4879-8dcb-a59cc8407860",
  "4cb260ec-d0b3-4cbc-a0be-16abb592233e",
  "2c52c755-6d4d-4df8-a685-c6b5503377bd",
  "cb2f8ea2-875d-471d-8242-edada08179a4",
  "f72bb38e-272e-4efb-848d-ba4fec308320",
  "b570cd51-23cf-4437-af04-bfe4d0e9e4a3",
  "53d6e5bf-8823-46c5-b346-035615fccd6f",
  "fd0be47c-5706-4005-9d47-ce067bc1ba20",
  "5444e70e-10a3-4fca-9619-601bfb32c6dc",
  "0b564ba8-1ca2-4260-aaab-d238f5b16b26",
  "264c8701-36d3-4623-8ffe-1d31ae7101f2",
  "446db346-4fc0-4d62-aa7b-c71a544416a0",
  "293c22e7-0290-43e7-9f10-5f8dac1f208a",
  "a5bc15d5-af6e-448b-9411-3d042bbc19ad",
  "d481e8f4-e5b3-498b-a9aa-e089210fde76",
  "5a1521cd-e3ff-4566-a2ce-2f2f57809293",
  "f39f7b15-0f98-4270-ad74-c38bea70e994",
  "35b1863d-43e5-4516-a60a-09acdf91650d",
  "d7f5aa77-bee6-4522-a008-52b2d6bd527a",
  "ef6a6b4a-13ee-4bfa-b907-5456a688e435",
  "ae4d1a38-4a42-4074-abf2-10fc330a796e",
  "a5eca37d-02f1-4aee-8329-17957b18d221",
  "106b4b88-f73a-4145-8c8f-885c3757ab78",
  "19acdbd0-e79a-4d24-aa03-d267303cb695",
  "c91d89fe-cd05-4da1-84e6-216bd967e7c3",
  "47982097-6a3f-4423-a11d-b5b37e48c3a1",
  "860d30e4-fb21-44aa-88e3-f693705c9dc7",
  "2ab60aa0-ff94-4899-83ec-0c7fb5ee04f3",
  "38a303b6-ef20-4471-a607-44964a7e9dd4",
  "c5e8044a-eadb-4175-a829-59705088eb84",
  "8c585246-f742-4838-8b1d-7e435f1e14e6",
  "55bf7a83-1815-4325-892a-fea2093f2841",
  "c1896e90-98c9-4b15-9e8d-20ac22dc4030",
  "8be8cddd-7797-4562-8aca-e6f9689ce390",
  "007e87fe-7b4f-47a5-9366-6bf249dfd648",
  "6a60cf14-6849-4751-b2c0-569f9fee30bf",
  "f8f26413-6f81-4e26-9ec3-7552221125dd",
  "2ae0e2f1-9404-4c8f-8322-2fb838d1f9f2",
  "37c1e3d7-4727-400c-8178-84fde16d0345",
  "f35e6f71-0fdf-4cfe-b1de-52b889fb7347",
  "e1e587d9-7bd3-4d7b-b52b-7613762d63e2",
  "71573c87-403e-4847-b68d-bbbe9ad11887",
  "71b4b1a6-7fff-4b5d-bd6a-c2be05430fac",
  "b8354951-1117-44b3-82cf-eac13bb64f5e",
  "c881f8e6-d502-4a4a-9a55-97236fd70024",
  "366856db-db60-4ea3-bd3b-5b4a31ae0f61",
  "523d5bc6-9d47-40df-a1d6-4e1bd7cfe28d",
  "4a7beb29-b445-4ff9-980e-165f3789f6ae",
  "5cb92c95-764e-4bec-adbd-ffc0560ee6b8",
  "1467be71-fb52-40ad-984a-2e82ae7f5236",
  "0fe2177f-2a1a-4a54-8229-c20781ee98f6",
  "0861d594-436e-4352-bdc1-cb6b475b2f66",
  "70559a25-01f1-40eb-86c0-cc3f0896d30a",
  "c2befd71-c1c8-4a6a-911d-9a8afa3a8dc6",
  "75f894e1-7fc1-48a5-8f6b-90818165c456",
  "05c16106-5ca2-472b-bd23-36cee34dea49",
  "d2a8002b-c6f9-447c-a95f-96d9a02e8c3b",
  "d6992315-f418-4096-be57-6d0d98f9d9c3",
  "98e70520-1669-4a1f-9f5e-39d37b749e70",
  "f653171a-f112-40fb-8628-ce1d012ec240",
  "6d4b1661-5d13-479a-93d4-db5cb8a46e3b",
  "2691c0bb-314c-4e4f-a94e-6ec4231b0283",
  "f4f6edb3-2a45-4ca2-a6d8-424a20d3db5b",
  "a2ac001f-e2dd-49b6-8312-fe23f2dfa8c8",
  "a314a751-221e-464f-b9d7-c979e447f1b1",
  "2fa2a1ec-2ed7-4c58-8a5e-87423b4c607e",
  "6c29bc31-ef0e-4731-923f-32d91db9a1e8",
  "524f62e2-ac3b-4c73-8059-63bc3f4e633c",
  "3656342b-8eeb-40e6-b9aa-558d16427d1d",
  "2937ac4c-65de-4dca-ba02-f742c7436ca7",
  "9a9d052d-08ed-4703-953e-34870c17e593",
  "b0c3846c-38dc-4236-89c0-1ff1ba8c370c",
  "39103740-6102-4840-bd0a-d178e350c2c9",
  "758229bf-a918-460c-8e79-8c18b9a9d427",
  "88e75794-5582-4a8a-aa3f-ccf214de1f83",
  "9f9e9f66-9fe8-4259-a6ed-af3879c32400",
  "79b4dcb2-1d79-48da-96fe-2460cc242142",
  "4a5a7d6a-7d45-4a22-a3d7-3f249ebe2f54",
  "43341c10-9232-4c5c-b0cf-48c5329b32c4",
  "17b76bb8-8644-488a-9897-b8ce2791f8b5",
  "bf039eb6-eb2b-488c-a97f-c469147c442f",
  "3df1a354-1629-4ef5-80a7-cf9e65eafe35",
  "0f4664e8-2fff-40c6-b512-48d75e07ba80",
  "85965cec-49e9-4858-b9ac-21b705be29e8",
  "edeca49b-cd07-4f44-a78c-ed88828c7007",
  "ff58965b-1743-48ac-bf0f-8daa0dee524b",
  "4e608956-7a50-4053-827b-b509e5c4f149",
  "9a66ed64-b40a-421c-b58e-7d2214a5601c",
  "11b2b172-2b76-48e9-b9a8-4606a6dd9888",
  "5b2a2de2-4bbb-40d0-9aeb-95f375b69267",
  "00a9b8a2-5ec2-407f-b6b5-bdf456962679",
  "1fc20ae8-ec39-409a-8a73-2731c17141d1",
  "b9ab3ca1-63da-4149-ab28-367cc5fad039",
  "5656a2fd-3614-4188-83c3-b66fafad4f2b",
  "3837f986-dce1-484d-bb4e-02954a3583d8",
  "0bd76f85-0ebe-4544-b5fe-a0241d27325e",
  "6fc3a1ea-b975-4882-ab29-b4d8057183b4",
  "2f1db32d-b8ec-4db6-ac29-39513201cceb",
  "6d76e5c9-6053-4a5f-a072-845ab12616a4",
  "8427db3b-b2ef-4a19-92a5-f6f0603be2ad",
  "729f1f52-5ced-4c27-8f69-46ee6964acf3",
  "60fb649f-7b7a-4696-873c-87bbd0ea6212",
  "99d64841-432a-4e17-b645-8398c4b6c51e",
  "68c16187-a112-4f50-bd2d-7bc2b0f37c52",
  "1b3be980-246c-45db-a2fb-7517f9f04188",
  "eed0d1bb-abde-4c58-a04d-f9fe1e85942d",
  "6beacaae-a128-43c7-87e8-f8691665d13c",
  "3a63c077-46b1-4f9a-bd99-34c9cee76550",
  "06e9cd44-df71-4236-bd80-5c8eb30c0345",
  "33a7b222-1118-4ba3-a6cc-3a053a2068c5",
  "c7755009-9189-4379-a7e6-25cfd08fc31a",
  "feeec83a-00cc-4492-bf18-bd519e9445bf",
  "230c2684-33b1-4352-831c-dae967d584da",
  "7ff00a2a-579e-4058-8f82-f8858d08c405",
  "e71e7072-6108-47bf-a047-fdb1c3e7a6cd",
  "07518670-bd95-499f-aae8-e7a91521562a",
  "78090d89-c1fe-4a98-aaa7-4ff46cd498ea",
  "adbb9fce-127c-40de-ada9-850ce63af888",
  "c2b3ca96-0e61-4f5b-9ed3-02c6907fde7c",
  "626f5aea-4347-4ad4-84d1-0c31ad2dcd7b",
  "538ec185-b4b4-474c-aa18-abf480834f51",
  "d60713d4-8b58-41d2-93fc-0719cfdbb859",
  "47e413e3-1f72-4c72-b901-58def7c3b2c6",
  "1d9b488e-e16b-4f58-acdb-4953668d7e50",
  "d16191d4-bc33-4c5e-811d-6f8c19c87562",
  "782cf249-2cc3-4cda-9fd0-e495679b6ab8",
  "ebda4696-54e3-40b6-a672-b016873d4905",
  "db7aadd0-caba-4d06-aaa0-73b332789060",
  "f34dd886-32d2-4ca6-a64c-ca45893c960f",
  "e8763970-3e91-471c-93e2-c7516707c941",
  "ffeb0dd1-ca1e-44a0-8e16-a96872043beb",
  "39be369e-cd29-4434-ba4d-38a772b7df16",
  "ab2e28d9-0b74-43a9-b5bb-bc74653ce03e",
  "dd3d9a2d-60b9-41c4-8761-24e24e765bc1",
  "e53cdd6a-eb8d-4645-a9dd-8b66e6ab62c9",
  "844bcab5-c1da-453c-af80-1789bbf46e87",
  "649a2c72-9a86-4a41-8d09-a6997364301b",
  "331e4e4d-f6b2-4489-9013-c0440695198c",
  "46f070d0-3ab4-4c72-b487-ea88eee1e7ef",
  "42e6cf15-3428-4123-a0ca-71ef6dd2f7c5",
  "2aa9865d-1faa-442b-890a-ceba2276637b",
  "102951bb-dc53-4a76-8593-07d45f022df7",
  "9eaf58c9-99eb-4c9f-ba93-51917951cfa7",
  "3ef2ac37-17ce-4551-a1b5-69ddcf5a6db4",
  "68ba3e46-f788-45e4-86ee-3f73c2480c35",
  "65907567-392e-4fc2-941e-82169b86b8a9",
  "3cefcd3a-c0d9-40d0-b9e8-5c3b6d1c836e",
  "0c283542-65db-4cf9-a58a-3bbdfecc1bea",
  "5cb1b655-7039-478f-9946-36d165b4c896",
  "9376bea6-f72a-4b73-87bd-21584391e865",
  "1b77ff50-6628-4422-916a-6877d68b158e",
  "b18f3145-3653-41b2-bc73-a9933149c596",
  "9ee91631-0d5b-4850-a61f-03f5d374a501",
  "1dee03bb-5939-4aeb-9e98-ed462e080ec6",
  "5677f168-34eb-4305-9118-43ae3a330b53",
  "0f570d34-ccd4-4450-b147-0bd1fa3288c6",
  "962af319-3e00-4f45-856e-06c342a7afe5",
  "fb6acef7-c111-49d5-87e3-0c84fa130fec",
  "8b5e7035-aaf0-4f3e-b4e6-f89cdf1c47da",
  "c603adcd-8a78-4ee9-84cb-282335900353",
  "b27bac8c-270d-4c99-86fe-39d9b104bd0e",
  "29616574-0ed5-4428-bea4-73bbff12ea47",
  "dda4088e-c15f-4f98-95e8-d769232620fe",
  "b03a65d4-13fd-4ee0-b557-6d9c758d7a8f",
  "799fa5fe-17ff-4c79-bf75-5fb81812f627",
  "bfb4a3f1-c7b0-42bd-a54a-fea9e724e89f",
  "84452932-4e32-4ca8-89a8-5cbaf4ca4b9e",
  "50a6dbfc-1a42-4288-97a3-401d5ad62f08",
  "f615af95-e29e-494e-9d88-d9d4eb9d90e0",
  "cd28c387-4f9d-4633-b5a9-ae5aac96ad80",
  "dd6fba68-5a56-4d08-b39c-df489d6fbe32",
  "930ceab4-d0c6-4f2c-9cee-c0a53f83b2b7",
  "b714e1ed-d0d0-4d2b-bb35-041ff712462c",
  "1cd33a99-934c-4f34-81bb-a9b9c09014a0",
  "e538d4df-e756-41d1-be5a-b23303906eae",
  "f43a9718-1456-46d4-bb6c-37dc0b7bdf42",
  "9390928b-28d6-4d0a-85e9-424710e228b3",
  "7173bb09-bc6b-4a6d-90bc-e9e80cebc2b4",
  "6f85b449-ca2e-4ac7-b1f9-b1014286c8dd",
  "38f5071a-c50d-4aa4-9f82-a7210ecbe56b",
  "ec215a4a-25a3-4009-ad50-15d8842b2564",
  "127ed529-1db4-4014-8e82-17bacb57c693",
  "7ca8395f-9c4b-4183-a8a6-3f8cb3fe6a68",
  "20e7cf9c-eb2d-479b-90da-4a2aad273ddb",
  "16c37cc1-2bc8-4380-a85b-286efd7be345",
  "4209792b-2bce-4122-ac86-1077871ee0bd",
  "7294cfc9-36df-4007-832c-be3b1391428a",
  "4053cafa-37b1-4c94-9eca-dc82b90c6aef",
  "77b985af-2509-4797-89f0-a4bc4b865362",
  "b320e2dc-cd0c-43ab-8941-de7782e857bb",
  "c45ba3c2-81bc-4759-add8-7a959c509558",
  "61071978-7890-4477-8bd9-edd73bacf398",
  "4a6eaf0a-fbdd-4ecd-bfc3-4c570a693e7a",
  "c64d1d0d-52d0-4a70-a641-93d9fee2d38c",
  "53d5f14e-681f-41fc-aaf9-2896fde1b4d8",
  "d3482bae-8266-4e47-b19b-2fddab713495",
  "5c613a35-8fee-413c-993f-1c0fa81ac35d",
  "bbb66299-8b2e-4458-9d69-4cbe17833138",
  "b0aa28bb-02d8-4a7c-abdf-92be0012cd61",
  "d2674062-85c6-4fa4-bf1f-65056448da17",
  "7d3717f3-397c-4764-9a4d-856b7ca34ec9",
  "3dfa7a7e-dde9-4666-9141-3f754f681c57",
  "2918230f-6e5b-4cc2-a78c-2bb173cff68a",
  "364115b7-9060-45da-af4f-1c5c96b9153b",
  "cc7c5075-f197-4ddb-8838-8ee6fbed1e38",
  "fd15e477-990d-4d1d-8bd7-6a3ac5730704",
  "616fe636-563b-4148-b740-9a3389413223",
  "94836d8e-1c31-4e27-a61f-ecf217f606d4",
  "972cd973-d016-46ac-aae6-dcfb41a5211e",
  "1993b2ce-7f9e-4668-ac4b-73b475697d43",
  "280a0f75-1bc9-465a-9b5b-e498542aedb2",
  "fe523de1-b5ab-4cf5-b6b3-23e1ad3aa262",
  "daab8c08-e279-4ed7-b307-bc1d885ad79d",
  "b2abde8f-bfc7-43b8-b0e7-ae0bb3815edd",
  "2f50ec14-0a3b-424b-9469-c1da9ae6a768",
  "8ce340cb-e09b-4ddb-9552-f2fa36be4a9e",
  "7a206fd3-6f35-4379-b1d3-e2dc625304f7",
  "c1657213-12fd-425f-b964-d2f41fb757de",
  "e54ad3db-20b6-439f-8eb5-f5d754dad951",
  "e9b7327e-b5f8-47ff-a438-d88fdb2ee198",
  "eda1f8de-2f84-484e-8ddf-d941084dca28",
  "0dd7ce19-f8e6-4fe9-992c-c4824dc58d7c",
  "afd6a674-b00a-4a0b-ad03-38f027f64b46",
  "4bd7cf37-e3c0-417c-993e-d037876753c9",
  "8c90f963-8a14-4eec-831d-a86d063fa789",
  "8a29bcaf-43d2-4faf-a364-4b2cf0416b2c",
  "85df6fe9-7fc3-4eaf-8126-5af7baa2bc46",
  "ab11dcad-d457-4218-99ac-9a87d7834d57",
  "56a55874-e426-4ee2-babb-6803e00d0884",
  "34e70ed7-cf55-41a9-bdf1-8bec8ce8df45",
  "1fd282c7-7a77-4603-8a12-f927469245dd",
  "e0c46bc9-9b62-4b9a-b882-5a70a42b0c21",
  "69d62ef2-1d84-4d0c-9dc7-b96055e3d294",
  "1045782e-fabb-4cb4-82e7-d848ea01c18f",
  "9cc5f2bc-c0d7-4196-99dd-2586d482689b",
  "c91d47bc-2c1c-4219-9552-49d7db21a17a",
  "ed8351eb-b711-4b98-aa9d-5b86ab5485af",
  "d3ddfbde-1feb-4046-bb25-797af7e3cfd4",
  "0db9d535-75bc-49fa-b73e-4e784ff94b65",
  "9c01aefa-0985-4685-9a57-014b62b67024",
  "cb01b3f9-62cd-4bef-98d3-7bcf2532d459",
  "d07bc540-bfca-48dd-a0c5-151f687b397a",
  "3af579e4-320c-45a8-919b-ff7305e3c847",
  "c113cd9a-de71-47ac-b40e-6cb80d5a6397",
  "888b5b03-1459-41af-ab7a-59f83f645d7c",
  "fe7b42dd-c3e9-49de-a0f5-f244c26fe4ca",
  "995ad6bd-3dd0-475f-b890-b9e5bea5f71e",
  "78316a0c-12d2-4ac9-b20d-1b06e7345e30",
  "f7f530d0-f4f0-4eb9-868e-21f93759119e",
  "4cde7399-8874-4bde-91db-77e652fa6a55",
  "888abb5b-f171-47ad-8e6a-9fdd622c9555",
  "4b3d5469-8d97-4886-a7f8-9e54a72e209f",
  "377d3fbb-273d-4961-9bf8-55e6542e94f6",
  "e9a1cd07-37f2-4f52-93cf-7090ab37808e",
  "3625ed9b-af37-4ca0-83b9-8e871f75d8ce",
  "0e49d190-631d-472a-82f4-a21d567c9329",
  "b47a8af9-39e4-4f81-8baa-e3c42de9c8e5",
  "3325e893-8531-4d6a-95a9-21de127494d6",
  "6979a4d5-74de-4978-8656-5a5dea70afe6",
  "23b3518a-8b7e-4197-8062-79d82481777f",
  "b7f8a869-805c-48e6-858b-5989ae7b57f0",
  "d1aacbec-1846-4f78-a996-eaea99314fd2",
  "f8e60d67-dfbb-4511-895e-c60c20055e52",
  "54d5a424-c375-4b9f-be0d-c78ccc288f6c",
  "71849e8b-3be7-4e0d-abaf-ce03240eec5e",
  "bfe2dfd9-7c94-43c3-81c2-922c185637b7",
  "d40e9597-6260-42fe-9fbf-1843a9d05ab6",
  "3cdc0b8d-f49f-4bb0-b205-955575d40b4e",
  "561642cd-7ba0-4efb-b4d0-200f22472c98",
  "2e3fe096-22c3-45cd-9a3c-3d8a142617a6",
  "58986880-8254-451a-8cd5-9bb29af31deb",
  "27feb213-deac-4b77-9ab1-c9dc965942c0",
  "7bd630be-1dd6-4731-b539-ad2860f943eb",
  "7e542773-3431-4384-bc51-b9dc63ffd034",
  "c3454c07-fc61-4558-be40-bdc5db9a34b6",
  "31c53ca6-2dee-45c5-bcdb-2e966b8dcfe3",
  "164de49c-3807-4b40-bb5a-48d820e4b635",
  "d1a37e3b-594d-4874-9c0e-695a76e576ee",
  "08c9284a-e0e1-4d29-9701-bee729d6d67a",
  "e738c622-fbfb-490c-b4b3-253603c704f5",
  "9e9b0ddf-5a22-468e-9a2b-40a19f310fba",
  "6d6c3747-c25c-4e1e-b07c-e29874d01a71",
  "6e492cf1-c8bb-4e58-baa5-c071648839f0",
  "52be3ece-3602-4f3a-8b9f-ef48342185f6",
  "c25010e9-a363-4c11-a1e2-c57ed74d56c7",
  "fff7dd5d-1318-497e-962c-36a088351b3d",
  "f4904b31-deec-42f7-967b-c6928dc825f7",
  "9bb2b674-54ab-49c0-ac17-37b91e10eaff",
  "9505e9e5-d4b6-4dc7-b227-b299cfb56bdc",
  "0102733f-e672-4153-88fe-554c7564de04",
  "ccffa648-a5d2-4dc1-966d-34df8429a868",
  "f4e4f7b0-70e9-47af-bdb8-187499ec3480",
  "aa8770e1-15e1-4739-a64a-712bb3367396",
  "0a1841a9-fd01-4e4e-b901-63345b01be5c",
  "ab2576c9-ad9b-4aab-90be-49e65f5d6674",
  "870f10ba-3817-4fb8-ba7d-14f9ce9fd044",
  "b74e701b-0a4f-400a-940d-627d61a0264e"
]

# MongoDB Aggregation Pipeline
pipeline = [
    {
        "$match": {
            "id": {"$in": MY_LIST},
            "tables.transactions": {
                "$elemMatch": {
                    "$or": [
                        {"Transfer from": {"$ne": ""}},
                        {"Transfer to": {"$ne": ""}}
                    ]
                }
            }
        }
    },
    {
        "$unwind": "$tables.transactions"
    },
    {
        "$match": {
            "$or": [
                {"tables.transactions.Transfer from": {"$ne": ""}},
                {"tables.transactions.Transfer to": {"$ne": ""}}
            ]
        }
    },
    {
        "$lookup": {
            "from": "documents",  # Specify the collection to join.
            "localField": "id",   # Field from the input documents.
            "foreignField": "id",  # Field from the documents of the "documents" collection.
            "as": "document_details"  # Output array field with the joined documents.
        }
    },
    {
        "$unwind": "$document_details"  # Unwind the results of the lookup to merge document details
    },
    {
        "$project": {
            "_id": 0,
            "id": 1,
            "transaction": "$tables.transactions",
            "beginning_bates": "$document_details.beginning_bates",
            "ending_bates": "$document_details.ending_bates",
            "classification": "$document_details.classification",
            "title": "$document_details.title"
        }
    }
]

# Execute the aggregation pipeline
transactions_with_transfer = extendedprops_collection.aggregate(pipeline)

# Iterate through the results and do something with them
for document in transactions_with_transfer:
    print(document)