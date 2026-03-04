import cv2
import mediapipe as mp
import pyautogui
import math

#Inicjalizacja mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

#Pobieranie rozdzielczości ekranu
screen_w, screen_h = pyautogui.size()

#Zmienne do wygładzania ruchu
smoothening = 3
prev_x, prev_y = 0, 0 
current_x, current_y = 0, 0

cliked = False

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Nie można odczytać obrazu z kamery.")
        break
    #Lustrzane odbicie obrazu
    frame = cv2.flip(frame, 1)
    #Konwersja do RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            #Rysowanie punktów i połączeń na dłoni
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            #Sterowanie kursorem czubkiem palca wskazującego
            index_finger = hand_landmarks.landmark[8]
            #Przeliczanie pozycji palca na piksele ekranu
            cursor_x = int(index_finger.x * screen_w)
            cursor_y = int(index_finger.y * screen_h)
            
            #Wygładzanie ruchu
            current_x = prev_x + (cursor_x - prev_x) / smoothening
            current_y = prev_y + (cursor_y - prev_y) / smoothening
            
            #Przesunięcie kursora
            pyautogui.moveTo(current_x, current_y, _pause=False)

            #Aktualizacja pozycji
            prev_x, prev_y = current_x, current_y

            #Kliknięcie za pomocą kciuka i palca środkowego
            thumb = hand_landmarks.landmark[4]
            middle_finger = hand_landmarks.landmark[12]
            
            distance = math.hypot(thumb.x - middle_finger.x, thumb.y - middle_finger.y)
            if distance < 0.05:
                if not clicked:
                    pyautogui.click()
                    clicked = True
                    #Wizualizacja
                    h,w,c = frame.shape
                    cx, cy = int(middle_finger.x * w), int(middle_finger.y * h)
                    cv2.circle(frame, (cx, cy), 15, (0,255,0), cv2.FILLED)
            else:
                clicked = False
    
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()