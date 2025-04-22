from deepface import DeepFace

#results = DeepFace.find(
    #img_path="static/uploads/grete/grete.jpg",
    #db_path="static/uploads/",
    #enforce_detection=False
#)

#print("Test find result:", results)

DeepFace.analyze(img_path="static/uploads/grete/grete.jpg", enforce_detection=False)
