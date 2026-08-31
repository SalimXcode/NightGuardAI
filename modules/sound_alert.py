import pygame
import threading
import os
import time
import math

class SoundAlert:
    def __init__(self):
        """Initialize sound system"""
        try:
            pygame.mixer.init()
            print("🔊 Sound system initialized!")
        except Exception as e:
            print(f"⚠️ Sound init error: {e}")
        
        self.is_playing = False
        self.sound_file = None
        self.use_generated = True
        
        # Check for siren file
        siren_path = "assets/sounds/siren_sound.mp3"
        if os.path.exists(siren_path):
            self.sound_file = siren_path
            self.use_generated = False
            print("🔊 Siren sound file loaded!")
        else:
            print("🔊 No siren file found - using generated sound")
            self.use_generated = True
    
    def generate_siren(self, duration=3):
        """Generate a simple siren sound"""
        try:
            sample_rate = 44100
            freq1 = 440
            freq2 = 880
            
            samples = []
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                freq = freq1 + (freq2 - freq1) * (0.5 + 0.5 * math.sin(2 * math.pi * 2 * t))
                value = int(32767 * 0.3 * math.sin(2 * math.pi * freq * t))
                samples.append(value)
            
            import array
            sound_array = array.array('h', samples)
            
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play(-1)  # Loop
            self.is_playing = True
            
            def stop_sound():
                time.sleep(duration)
                sound.stop()
                self.is_playing = False
            
            threading.Thread(target=stop_sound, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ Sound generation error: {e}")
            return False
    
    def play_siren(self, duration=3):
        """Play siren sound"""
        if self.is_playing:
            print("🔊 Siren already playing!")
            return False
        
        print("🚨 PLAYING SIREN! 🔊")
        
        if self.use_generated:
            return self.generate_siren(duration)
        else:
            try:
                pygame.mixer.music.load(self.sound_file)
                pygame.mixer.music.play(-1)  # Loop
                self.is_playing = True
                
                def stop_sound():
                    time.sleep(duration)
                    pygame.mixer.music.stop()
                    self.is_playing = False
                
                threading.Thread(target=stop_sound, daemon=True).start()
                return True
            except Exception as e:
                print(f"❌ Sound play error: {e}")
                return False
    
    def stop(self):
        """Stop any playing sound"""
        if self.is_playing:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
            except:
                pass
            self.is_playing = False
            print("🔊 Sound stopped")

# Test
if __name__ == "__main__":
    sound = SoundAlert()
    print("Playing siren for 3 seconds...")
    sound.play_siren(3)
    time.sleep(4)