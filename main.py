from raylib import *
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"MisInput - Keyboard Betrayal")
InitAudioDevice()
SetTargetFPS(60)

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

current_state = STATE_MENU

menu_sound = LoadSound(b"Media/menutheme.wav")
game_sound = LoadSound(b"Media/Context Sensitive - 20XX - 01 Thermal.wav")
over_sound = LoadSound(b"Media/Context Sensitive - 20XX - 03 20XX.wav")
click_sound = LoadSound(b"Media/click.wav")
PlaySound(menu_sound)

word_bank = [
    "the quick brown fox jumps over the lazy dog",
    "please do not microdose the corporate cold brew",
    "my keyboard is perfectly fine and i am stable",
    "whoever invented group projects deserves detention",
    "this sentence would be easier if keys stayed put",
    "mitigate the risk of catastrophic typographical errors",
    "unauthorized software modifications detected in core systems",
    "hypertext transfer protocol secure connection interrupted",
    "automated response systems have failed to initialize",
    "please contact your local system administrator immediately"
]

current_target = ""
player_input = ""
score = 0
phrases_completed = 0
game_timer = 60.0
timer_active = False

juice_timer = 0.0
cursor_visible = True

shake_timer = 0.0
shake_intensity = 0.0

combo_streak = 0
max_combo = 0
score_multiplier = 1

flash_alpha = 0.0
floating_texts = []

mutations = {}
available_keys = list("abcdefghijklmnopqrstuvwxyz")
status_message = "SYSTEM STATUS: Keyboard functioning optimally... for now."

slider_value = 0.5
slider_dragging = False
slider_bounds = {"x": 50, "y": 620, "w": 200, "h": 20}

while not WindowShouldClose():
    
    delta_time = GetFrameTime()

    juice_timer += delta_time
    if juice_timer >= 0.5:
        cursor_visible = not cursor_visible
        juice_timer = 0.0
    
    mouse_pos = GetMousePosition()

    dx = 0
    dy = 0
    if shake_timer > 0.0:
        shake_timer -= delta_time
        dx = random.randint(int(-shake_intensity), int(shake_intensity))
        dy = random.randint(int(-shake_intensity), int(shake_intensity))

    if flash_alpha > 0.0:
        flash_alpha -= delta_time
        if flash_alpha < 0.0:
            flash_alpha = 0.0

    for text_mode in floating_texts[:]:
        text_mode["y"] -= delta_time * 40.0
        text_mode["alpha"] -= delta_time * 1.5
        if text_mode["alpha"] <= 0.0:
            floating_texts.remove(text_mode)

    if current_state == STATE_MENU:
        if not IsSoundPlaying(menu_sound):
            PlaySound(menu_sound)
            
        if IsKeyPressed(KEY_ENTER):
            StopSound(menu_sound)
            PlaySound(game_sound)
            current_target = random.choice(word_bank)
            player_input = ""
            score = 0
            phrases_completed = 0
            combo_streak = 0
            score_multiplier = 1
            game_timer = 60.0
            timer_active = True
            mutations = {}
            available_keys = list("abcdefghijklmnopqrstuvwxyz")
            status_message = "SYSTEM STATUS: Keyboard functioning optimally... for now."
            current_state = STATE_PLAYING

        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            if (mouse_pos.x >= slider_bounds['x'] and mouse_pos.x <= slider_bounds["x"] + slider_bounds['w'] and 
                mouse_pos.y >= slider_bounds['y'] and mouse_pos.y <= slider_bounds['y'] + slider_bounds["h"]):
                slider_dragging = True
        
        if IsMouseButtonReleased(MOUSE_BUTTON_LEFT):
            slider_dragging = False

        if slider_dragging:
            slider_value = (mouse_pos.x - slider_bounds["x"]) / slider_bounds["w"]
            if slider_value < 0.0: slider_value = 0.0
            if slider_value > 1.0: slider_value = 1.0
            SetMasterVolume(slider_value)
            
    elif current_state == STATE_PLAYING:
        if timer_active:
            if not IsSoundPlaying(game_sound):
                PlaySound(game_sound)

        if timer_active:
            game_timer -= delta_time
            if game_timer <= 0:
                game_timer = 0
                timer_active = False
                StopSound(game_sound)
                PlaySound(over_sound)
                current_state = STATE_GAMEOVER

        key = GetKeyPressed()
        while key > 0:
            if (key >= 32) and (key <= 125) and (len(player_input) < 60):
                char_pressed = chr(key).lower()
                
                if char_pressed in mutations:
                    char_pressed = mutations[char_pressed]

                player_input += char_pressed
                PlaySound(click_sound)
                
                current_idx = len(player_input) - 1
                if current_idx < len(current_target) and char_pressed == current_target[current_idx]:
                    combo_streak += 1
                    if combo_streak > max_combo:
                        max_combo = combo_streak
                    score_multiplier = 1 + (combo_streak // 10)
                else:
                    combo_streak = 0
                    score_multiplier = 1
                    
            key = GetKeyPressed()

        if IsKeyPressed(KEY_BACKSPACE):
            if len(player_input) > 0:
                player_input = player_input[:-1]
            combo_streak = 0
            score_multiplier = 1

        if player_input == current_target:
            score += 100 * score_multiplier
            phrases_completed += 1
            player_input = ""
            current_target = random.choice(word_bank)
            
            game_timer += 5.0

            floating_texts.append({"text": "+5s", "x": 980, "y": 60, "alpha": 1.0})

            if len(available_keys) >= 2:
                k1 = available_keys.pop(random.randint(0, len(available_keys) - 1))
                k2 = available_keys.pop(random.randint(0, len(available_keys) - 1))
                mutations[k1] = k2
                mutations[k2] = k1
                status_message = f"LAYOUT WARNING: '{k1.upper()}' AND '{k2.upper()}' keys have swapped positions!"
                shake_timer = 0.4
                shake_intensity = 12.0
                flash_alpha = 1.0
            else:
                status_message = "CRITICAL: Complete keyboard infrastructure breakdown."

    elif current_state == STATE_GAMEOVER:
        if IsKeyPressed(KEY_ENTER):
            StopSound(over_sound)
            PlaySound(game_sound)
            current_target = random.choice(word_bank)
            player_input = ""
            score = 0
            phrases_completed = 0
            combo_streak = 0
            score_multiplier = 1
            game_timer = 60.0
            timer_active = True
            mutations = {}
            available_keys = list("abcdefghijklmnopqrstuvwxyz")
            status_message = "SYSTEM STATUS: Keyboard functioning optimally... for now."
            current_state = STATE_PLAYING
            
        if IsKeyPressed(KEY_ESCAPE):
            break

    BeginDrawing()
    ClearBackground(RAYWHITE)

    rlPushMatrix()
    rlTranslatef(dx, dy, 0)

    if current_state == STATE_MENU:
        DrawText(b"MISINPUT: WHO MOVED MY KEYS?", 260, 220, 50, MAROON)
        DrawText(b"Your layout will slowly corrupt itself every time you clear a sentence.", 280, 310, 20, DARKGRAY)
        DrawText(b"You have 60 seconds to clear as many targets as possible.", 360, 350, 20, DARKGRAY)
        DrawText(b"PRESS [ ENTER ] TO INITIALIZE INTERFACE", 370, 500, 24, BLACK)

        DrawRectangle(slider_bounds["x"], slider_bounds["y"], slider_bounds["w"], slider_bounds["h"], LIGHTGRAY)
        DrawRectangleLines(slider_bounds["x"], slider_bounds["y"], slider_bounds["w"], slider_bounds["h"], DARKGRAY)
        
        handle_x = int(slider_bounds["x"] + (slider_value * slider_bounds["w"]))
        DrawRectangle(handle_x - 5, slider_bounds["y"] - 5, 10, slider_bounds["h"] + 10, MAROON)

        volume_text = f"VOLUME: {int(slider_value * 100)}%".encode('utf-8')
        DrawText(volume_text, slider_bounds["x"], slider_bounds["y"] - 25, 16, DARKGRAY)

    elif current_state == STATE_PLAYING:
        score_text = f"SCORE: {score}".encode('utf-8')
        cleared_text = f"COMPLETED: {phrases_completed}".encode('utf-8')
        combo_text = f"STREAK: {combo_streak} (x{score_multiplier})".encode('utf-8')
        timer_text = f"TIME: {game_timer:.1f}s".encode('utf-8')
        
        DrawText(score_text, 150, 60, 22, DARKGRAY)
        DrawText(cleared_text, 420, 60, 22, DARKGRAY)
        DrawText(combo_text, 680, 60, 22, ORANGE)
        DrawText(timer_text, 980, 60, 22, MAROON)
        DrawRectangle(150, 100, 980, 4, LIGHTGRAY)
        
        DrawText(b"TARGET TEXT:", 150, 180, 18, DARKGRAY)
        DrawText(current_target.encode('utf-8'), 150, 220, 26, BLACK)

        DrawText(b"YOUR SYSTEM INPUT:", 150, 340, 18, DARKGRAY)
        
        for i, char in enumerate(player_input):
            char_x = 150 + (i * 15)
            char_bytes = char.encode('utf-8')

            if i < len(current_target) and char == current_target[i]:
                DrawText(char_bytes, char_x, 380, 26, LIME)
            else:
                DrawText(char_bytes, char_x, 380, 26, RED)

        if cursor_visible and len(player_input) < 60:
            cursor_offset = 150 + (len(player_input) * 15)
            DrawRectangle(cursor_offset, 380, 3, 26, DARKGRAY)

        box_color = ColorAlpha(MAROON, flash_alpha * 0.4)

        DrawRectangle(150, 520, 980, 100, LIGHTGRAY)
        DrawRectangleLines(150, 520, 980, 100, box_color)
        DrawText(status_message.encode('utf-8'), 180, 560, 18, DARKGRAY)

        text_color = MAROON if flash_alpha > 0.1 else DARKGRAY
        DrawText(status_message.encode('utf-8'), 180, 560, 18, text_color)

        credit_text = b"Music: Context Sensitive - [Thermal - 20XX]"
        text_width = MeasureText(credit_text, 16)
        text_x = SCREEN_WIDTH - text_width - 20
        text_y = SCREEN_HEIGHT - 16 - 20
        DrawText(credit_text, text_x, text_y, 16, DARKGRAY)

        for text_mode in floating_texts:
            particle_color = ColorAlpha(LIME, text_mode["alpha"])
            DrawText(text_mode["text"].encode('utf-8'), int(text_mode["x"]), int(text_mode["y"]), 22, particle_color)

    elif current_state == STATE_GAMEOVER:
        DrawText(b"INTERFACE DISCONNECTED", 360, 160, 45, RED)

        final_score = f"Final Achieved Score: {score}".encode('utf-8')
        final_cleared = f"Total Completed Phrases: {phrases_completed}".encode('utf-8')
        final_combo = f"Highest Input Streak: {max_combo}".encode('utf-8')

        DrawText(final_score, 420, 240, 24, DARKGRAY)
        DrawText(final_cleared, 420, 290, 24, DARKGRAY)
        DrawText(final_combo, 420, 340, 24, ORANGE)

        DrawText(b"PRESS [ ENTER ] TO RESTART INTERFACE", 390, 440, 22, DARKGRAY)
        DrawText(b"PRESS [ ESC ] TO TERMINATE SYSTEM", 420, 490, 22, DARKGRAY)

        credit_text = b"Music: Context Sensitive - [Chiptune - 20XX]"
        text_width = MeasureText(credit_text, 16)
        text_x = SCREEN_WIDTH - text_width - 20
        text_y = SCREEN_HEIGHT - 16 - 20
        DrawText(credit_text, text_x, text_y, 16, DARKGRAY)

    rlPopMatrix()
    EndDrawing()

UnloadSound(menu_sound)
UnloadSound(game_sound)
UnloadSound(over_sound)
UnloadSound(click_sound)
CloseAudioDevice()
CloseWindow()