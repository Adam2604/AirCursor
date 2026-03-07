import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time

#Inicjalizacja mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

#Pobieranie rozdzielczości ekranu
screen_w, screen_h = pyautogui.size()

#Zmienne do wygładzania ruchu
smoothening = 2
prev_x, prev_y = 0, 0 
current_x, current_y = 0, 0

clicked = False

#Zmienne do scrollowania
scroll_mode = False
prev_scroll_y = 0
scroll_sensitivity = 350

#Zmienne do gestu cofania (ściśnięcie dłoni)
fist_detected = False
fist_cooldown = 1.0 #Czas blokady po cofnięciu
last_fist_time = 0

#Margines aktywnego ekranu
margin = 120

def is_finger_extended(hand_landmarks, finger_tip_id, finger_pip_id):
    return hand_landmarks.landmark[finger_tip_id].y < hand_landmarks.landmark[finger_pip_id].y

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Nie można odczytać obrazu z kamery.")
        break
    #Lustrzane odbicie obrazu
    frame = cv2.flip(frame, 1)

    h,w,c = frame.shape
    cv2.rectangle(frame, (margin, margin), (w-margin, h-margin), (255,0,255), 2)
    #Konwersja do RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        has_second_hand = False
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            #Rysowanie punktów i połączeń na dłoni
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if i == 0:
                #Sprawdzanie stanu palców
                index_up = is_finger_extended(hand_landmarks, 8, 6)
                middle_up = is_finger_extended(hand_landmarks, 12, 10)
                ring_up = is_finger_extended(hand_landmarks, 16, 14)

                index_finger = hand_landmarks.landmark[8]
                middle_finger = hand_landmarks.landmark[12]

                if index_up and middle_up and not ring_up:
                    #Tryb scrollowania - dwa palce w górze
                    mid_y = (index_finger.y + middle_finger.y) / 2
                    mid_x = (index_finger.x + middle_finger.x) / 2

                    if not scroll_mode:
                        scroll_mode = True
                        prev_scroll_y = mid_y
                    else:
                        delta_y = prev_scroll_y - mid_y
                        scroll_amount = int(delta_y * scroll_sensitivity * 10)
                        if abs(scroll_amount) > 0:
                            pyautogui.scroll(scroll_amount, _pause=False)
                            prev_scroll_y = mid_y

                    #Wizualizacja trybu scroll
                    cx = int(mid_x * w)
                    cy = int(mid_y * h)
                    cv2.circle(frame, (cx, cy), 12, (255, 165, 0), cv2.FILLED)
                    cv2.putText(frame, "SCROLL", (cx + 20, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)

                else:
                    scroll_mode = False
                    #Sterowanie kursorem czubkiem palca wskazującego
                    #Przeliczanie pozycji palca na piksele ekranu
                    x1, y1 = int(index_finger.x * w), int(index_finger.y * h)

                    cursor_x = np.interp(x1, (margin, w-margin), (0, screen_w))
                    cursor_y = np.interp(y1, (margin, h-margin), (0, screen_h))
                    
                    #Wygładzanie ruchu
                    current_x = prev_x + (cursor_x - prev_x) / smoothening
                    current_y = prev_y + (cursor_y - prev_y) / smoothening
                    
                    #Przesunięcie kursora
                    pyautogui.moveTo(current_x, current_y, _pause=False)

                    #Aktualizacja pozycji
                    prev_x, prev_y = current_x, current_y

            elif i == 1:
                has_second_hand = True
                #Kliknięcie za pomocą złączenia kciuka i palca wskazującego drugiej dłoni
                thumb = hand_landmarks.landmark[4]
                index_finger = hand_landmarks.landmark[8]
                
                distance = math.hypot(thumb.x - index_finger.x, thumb.y - index_finger.y)
                if distance < 0.05:
                    if not clicked:
                        pyautogui.click()
                        clicked = True
                        #Wizualizacja
                        h,w,c = frame.shape
                        cx, cy = int(index_finger.x * w), int(index_finger.y * h)
                        cv2.circle(frame, (cx, cy), 15, (0,255,0), cv2.FILLED)
                else:
                    clicked = False

                #Gest cofania - ściśnięcie dłoni
                index_up2 = is_finger_extended(hand_landmarks, 8, 6)
                middle_up2 = is_finger_extended(hand_landmarks, 12, 10)
                ring_up2 = is_finger_extended(hand_landmarks, 16, 14)
                pinky_up2 = is_finger_extended(hand_landmarks, 20, 18)
                current_time = time.time()

                is_fist = not index_up2 and not middle_up2 and not ring_up2 and not pinky_up2

                if is_fist and not fist_detected and (current_time - last_fist_time) > fist_cooldown:
                    #Pięść wykryta - cofanie (Alt+Left)
                    pyautogui.hotkey('alt', 'left', _pause=False)
                    last_fist_time = current_time
                    fist_detected = True
                    #Wizualizacja
                    wrist = hand_landmarks.landmark[0]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)
                    cv2.putText(frame, "<< COFANIE", (cx - 60, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
                elif not is_fist:
                    fist_detected = False
                    
        if not has_second_hand:
            clicked = False
            fist_detected = False
    else:
        clicked = False
        fist_detected = False
    
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()