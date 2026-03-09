# 🖐️ AirCursor: Gesture-Based System Control

A real-time computer control system that transforms your hand into an intelligent controller. Instead of a traditional mouse, this project utilizes computer vision for precise gesture tracking, enabling navigation, content scrolling, and system actions without physical contact.

---

## 💡 How It Works

The system uses a standard webcam to capture video, which is then processed by machine learning algorithms to interpret movement.

### Core Logic:

1. **Image Capture:** An OpenCV-based module captures frames from the camera, applying a horizontal flip to make hand movements intuitive for the user.
2. **Hand Detection:** The MediaPipe library analyzes the image in real-time, identifying 21 distinct hand landmarks with high detection confidence.
3. **Gesture Interpretation:** The system evaluates the state of individual fingers (extended vs. folded) and their relative positions to recognize specific intents, such as scrolling or clicking.
4. **Action Execution:** Calculated coordinates are mapped to the screen resolution using interpolation, and the PyAutoGUI library executes physical cursor movements or keyboard shortcuts.

---

## 🌟 Key Features

### 🎯 Precision Cursor Control

The system maps the position of the index finger tip to screen coordinates, providing fluid navigation.

* **Active Margin:** A defined active zone (margin: 120) allows the cursor to reach the edges of the screen without the user's hand leaving the camera's field of view.
* **Movement Smoothening:** A smoothening algorithm eliminates hand jitter by calculating the cursor position as a weighted average of previous movements, ensuring stability.

### 📜 Smart Scroll Mode

Dynamic content scrolling activated by a specific hand configuration.

* **Gesture:** Extending both the index and middle fingers simultaneously toggles the system into scroll mode.
* **Sensitivity:** Scrolling speed is proportional to the vertical movement of the hand, allowing for rapid browsing of long documents or websites.

### 🖱️ Multi-Hand Interaction

The project supports simultaneous tracking of two hands, distributing functions for enhanced ergonomics.

* **Task Separation:** One hand is typically responsible for cursor positioning, while the second hand performs specific actions.
* **Pinch-to-Click:** Joining the thumb and index finger of the second hand generates an immediate left-mouse click.

### ⏪ "Fist" Protocol (Back Gesture)

An intuitive way to navigate backward in browsers or file explorers.

* **Logic:** Clenching the second hand into a fist (no fingers extended) triggers the system-wide shortcut Alt + Left Arrow.
* **Cooldown System:** A built-in `fist_cooldown` parameter prevents accidental multiple triggers of the "back" action.

---

## 🏗️ Tech Stack

* **Core Language:** Python
* **Computer Vision:** OpenCV (camera handling and parameter visualization)
* **Machine Learning:** MediaPipe (advanced hand and finger tracking)
* **UI Automation:** PyAutoGUI (simulating mouse and keyboard input)
* **Calculations:** NumPy (coordinate interpolation and mathematical operations)
