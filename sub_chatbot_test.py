import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(
    'ziptalk-chatbot-firebase-adminsdk-kz477-4cadf62941.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'ziptalk-chatbot',
})

db = firestore.client()

# docs = db.collection(u'subscription_info').where(u'realtime_info.date', u'==', '2021-01-18').stream()
docs = db.collection(u'subscription_info').stream()

# document(u'wSvEdEy9bryTK0cXtlmD')
# doc_ref.set(my_data)

# doc = doc_ref.get()

# if doc.exists:
#     print(f'Document data: {doc.to_dict()}')
# else:
#     print(u'No such document!')

text = ""
date = '2021-03-25'

for doc in docs:
    temp = doc.to_dict()

    if(temp["realtime_info"]["date"] == date):
        text = text + "날짜 : " + temp["realtime_info"]["date"] + "\n"
        text = text + "▼▼▼ 아파트정보 ▼▼▼" + "\n"
        text = text + "아파트명 : " + temp["realtime_info"]["apt_info"]["apt_name"] + "\n"
        text = text + "공급위치 : " + temp["realtime_info"]["apt_info"]["address"] + "\n"
        text = text + "공급규모 : " + temp["realtime_info"]["apt_info"]["sup_size"] + "\n"
        text = text + "문의처 : " + temp["realtime_info"]["apt_info"]["tel"].replace("\n", "") + "\n"
        text = text + "▼▼▼ 청약일정 ▼▼▼" + "\n"
        text = text + "모집공고일 : " + temp["realtime_info"]["sub_sch"]["ann_date"] + "\n"
        for sch in range(0, 3):
            if (temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["class_name"] != ""):
                text = text + "구분명 : " + temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["class_name"] + "\n"
                text = text + "해당지역 접수일 : " + temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["local_date"] + "\n"
                text = text + "기타지역 접수일 : " + temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["other_date"] + "\n"
                text = text + "접수장소 : " + temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["recept_place"] + "\n"
            elif (sch == 0 and temp["realtime_info"]["sub_rec"][sch]["class_name"] == ""):
                text = text + "접수일 : " + temp["realtime_info"]["sub_sch"]["sub_rec"][sch]["local_date"] + "\n"
        text = text + "당첨자 발표일 : " + temp["realtime_info"]["sub_sch"]["winner_date"].replace("\n", "").replace("\t", "") + "\n"
        text = text + "계약일 : " + temp["realtime_info"]["sub_sch"]["contract_date"] + "\n"
        text = text + "=================\n"

print(text)