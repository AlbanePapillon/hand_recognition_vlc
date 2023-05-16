import time
import cv2
import mediapipe as mp
import vlc

path = r'C:\Users\Albane\Pictures\Perso\debussy_arabesque_num_1.mp4'

# hand recognition
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

# VLC player
instance = vlc.Instance()
player = instance.media_player_new()

media = instance.media_new(path)
player.set_media(media)

played = False


def play_pause():
    global played
    if played:
        player.pause()
    else:
        player.play()
        played = True


def distance(a, b):
    return abs(a - b)


state = "unknown"
start_time = time.time()


def position(p):
    global state
    global start_time

    if state == "unknown":
        start_time = time.time()
        state = p
        print("unknown -> ", p)
    elif state != "hold" and (time.time() - start_time) > 0.3:
        action(p)
        state = "hold"
        print(time.time(), " : known -> hold")


def action(p):
    if p == "thumb_up":
        play_pause()
    elif p == "open_hand":
        global played
        if played:
            player.stop()
            played = False
        # exit(0)
    elif p == "zero_hand":
        print("mute")
    elif p == "victory_hand":
        print("forward")


def thumb_up(handLandmarks):
    return handLandmarks[4].y < handLandmarks[3].y \
        and handLandmarks[8].x > handLandmarks[6].x \
        and handLandmarks[12].x > handLandmarks[10].x \
        and handLandmarks[16].x > handLandmarks[14].x \
        and handLandmarks[20].x > handLandmarks[18].x


def open_hand(handLandmarks):
    return handLandmarks[4].x < handLandmarks[3].x \
        and handLandmarks[8].y < handLandmarks[6].y \
        and handLandmarks[12].y < handLandmarks[10].y \
        and handLandmarks[16].y < handLandmarks[14].y \
        and handLandmarks[20].y < handLandmarks[18].y


def zero_hand(handLandmarks):
    return distance(handLandmarks[4].x, handLandmarks[8].x) < 0.2 \
        and distance(handLandmarks[4].y, handLandmarks[8].y) < 0.2 \
        and handLandmarks[7].y < handLandmarks[8].y \
        and handLandmarks[12].y < handLandmarks[10].y \
        and handLandmarks[16].y < handLandmarks[14].y \
        and handLandmarks[20].y < handLandmarks[18].y


def victory_hand(handLandmarks):
    return handLandmarks[4].x > handLandmarks[3].x \
        and handLandmarks[8].y < handLandmarks[6].y \
        and handLandmarks[12].y < handLandmarks[10].y \
        and handLandmarks[16].y > handLandmarks[14].y \
        and handLandmarks[20].y > handLandmarks[18].y


def event_loop():
    global state

    prev_time = 0
    while cap.isOpened():
        success, image = cap.read()
        image = cv2.flip(image, 1)

        if not success:
            print("Ignoring empty camera frame.")
            continue

        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label


                # ranked from most to least restrictive
                if zero_hand(hand_landmarks.landmark):
                    position("zero_hand")
                elif thumb_up(hand_landmarks.landmark):
                    position("thumb_up")
                elif victory_hand(hand_landmarks.landmark):
                    position("victory_hand")
                elif open_hand(hand_landmarks.landmark):
                    position("open_hand")
                else:
                    state = "unknown"
                    print(" -> unknown")

                # Draw hand landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            state = "unknown"
            print(" no hand -> unknown")

        # calcul fps
        cur_time = time.time()
        fps = int(1 / (cur_time - prev_time))
        prev_time = cur_time
        text = "fps : " + str(fps)

        cv2.putText(image, text, (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
        # print(fps)

        # Display image
        cv2.imshow('MediaPipe Hands', image)

        # Echap
        if cv2.waitKey(1) == 27:
            break


# For webcam input:
cap = cv2.VideoCapture(0)
event_loop()
cap.release()
cv2.destroyAllWindows()