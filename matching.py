import face_recognition


def is_matching(img1, img2, thresh):
    """
    :param img1: imgage 1 path
    :param img2: image 2 path
    :return: bool , true if same person, else false

    """
    image_1 = face_recognition.load_image_file(img1)
    image_2 = face_recognition.load_image_file(img2)

    image_1_encoding = face_recognition.face_encodings(image_1)[0]
    image_2_encoding = face_recognition.face_encodings(image_2)[0]

    face_distance = face_recognition.face_distance([image_1_encoding], image_2_encoding)[0]
    return face_distance <= thresh


# print(is_matching("obama.jpg","obama2.jpg"))
