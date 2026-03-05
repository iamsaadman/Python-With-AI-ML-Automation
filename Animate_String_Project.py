# animate string project
# sys = In this case, we use it to directly write output to the console without adding a newline character.
# time = It allows us to pause the program using time.sleep() to create the animation effect.

import sys
import time

# Function to animate text character by character
def animate_text(text, delay=0.1):
    """
    Animates text by printing each character with a delay.
    
    Parameters:
    text (str): The text to animate
    delay (float): Delay between characters in seconds (default: 0.1)
    """
    for char in text:
        sys.stdout.write(char)  # Write the character to the console
        sys.stdout.flush()  # Flush the output buffer to ensure it appears immediately
        time.sleep(delay)  # Pause for a short time to create the animation effect
    print()  # Move to the next line after the animation is complete

# Animate the original welcome text
text = "🌟✨Welcome to python Magic ✨🌟"
animate_text(text)

# Create and animate star design pattern
print("\n")
star_pattern = [
    "        *",
    "       *.*",
    "      *...*",
    "     *.....*",
    "    *.......*",
    "   *.........*",
    "  *..........*",
    " *............*",
    "*...............*",
    " *............*",
    "  *..........*",
    "   *.........*",
    "    *.......*",
    "     *.....*",
    "      *...*",
    "       *.*",
    "        *"
]

print("Star Design Animation:")
for line in star_pattern:
    animate_text(line, delay=0.05)  # Animate each line of the star pattern with a longer delay for effect
