import random

SIZE = 5
MAX_MOVES = 15



player_x = 0
player_y = 0

treasure_x = random.randint(0, SIZE - 1)
treasure_y = random.randint(0, SIZE - 1)

while treasure_x == 0 and treasure_y == 0:
    treasure_x = random.randint(0, SIZE - 1)
    treasure_y = random.randint(0, SIZE - 1)


def show_map():
    print()

    for y in range(SIZE):
        for x in range(SIZE):
            if x == player_x and y == player_y:
                print(" P ", end="")
            else:
                print(" . ", end="")
        print()

    print()


def distance_to_treasure():
    return abs(player_x - treasure_x) + abs(player_y - treasure_y)


print("=== TREASURE HUNT ===")
print()
print("Find the hidden treasure!")
print("Controls:")
print("  W = up")
print("  S = down")
print("  A = left")
print("  D = right")
print("  Q = quit")

moves_left = MAX_MOVES

while moves_left > 0:
    show_map()

    print(f"Moves left: {moves_left}")

    distance = distance_to_treasure()

    if distance <= 1:
        print("🔥 The treasure is VERY close!")
    elif distance <= 3:
        print("🌡️ You're getting warmer.")
    else:
        print("❄️ It's cold here.")

    command = input("> ").lower().strip()

    new_x = player_x
    new_y = player_y

    if command == "w":
        new_y -= 1
    elif command == "s":
        new_y += 1
    elif command == "a":
        new_x -= 1
    elif command == "d":
        new_x += 1
    elif command == "q":
        print("Goodbye!")
        break
    else:
        print("Unknown command.")
        continue

    if not (0 <= new_x < SIZE and 0 <= new_y < SIZE):
        print("You can't go outside the map!")
        continue

    player_x = new_x
    player_y = new_y
    moves_left -= 1

    if player_x == treasure_x and player_y == treasure_y:
        print()
        print("💰 YOU FOUND THE TREASURE!")
        print(f"You had {moves_left} moves remaining.")
        break

else:
    print()
    print("💀 You ran out of moves.")
    print(f"The treasure was at ({treasure_x}, {treasure_y}).")