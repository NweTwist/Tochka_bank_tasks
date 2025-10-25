import sys
import heapq

ROOM_TYPES = "ABCD"
COST = {"A": 1, "B": 10, "C": 100, "D": 1000}
DOOR_POS = [2, 4, 6, 8]        # индексы дверей комнат в коридоре
HAL_LEN = 11
HAL_STOP_POS = {0, 1, 3, 5, 7, 9, 10}  # где можно стоять (не у дверей)


def parse_input(lines: list[str]):
    if len(lines) < 5:
        raise ValueError("Ожидается 5 строк диаграммы")

    corridor = lines[1]
    hallway = tuple(corridor[1:12])  # между стенами

    top_line = lines[2]
    bottom_line = lines[3]
    top = [ch for ch in top_line if ch in ROOM_TYPES]
    bottom = [ch for ch in bottom_line if ch in ROOM_TYPES]
    if len(top) != 4 or len(bottom) != 4:
        raise ValueError("Неправильный формат комнат")

    rooms = tuple((top[i], bottom[i]) for i in range(4))
    return hallway, rooms


def goal_state():
    hallway = tuple("." for _ in range(HAL_LEN))
    rooms = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    )
    return hallway, rooms


def path_clear(h: int, d: int, hallway: tuple[str, ...]) -> bool:
    if h < d:
        for i in range(h + 1, d):
            if hallway[i] != ".":
                return False
    else:
        for i in range(d + 1, h):
            if hallway[i] != ".":
                return False
    return True


def generate_moves(state):
    hallway, rooms = state

    # Ходы: из коридора в комнату
    for h_pos, amph in enumerate(hallway):
        if amph == ".":
            continue
        r_idx = ord(amph) - ord("A")
        door = DOOR_POS[r_idx]

        # Путь по коридору до двери должен быть свободен
        if not path_clear(h_pos, door, hallway):
            continue

        room = rooms[r_idx]
        # Здесь в комнату можно входить только, если там нет чужих типов :))))
        if any(c != "." and c != amph for c in room):
            continue

        # Садимся на самую глубокую свободную позицию
        if room[1] == ".":
            depth = 1
        elif room[0] == ".":
            depth = 0
        else:
            continue  # нет места

        steps = abs(h_pos - door) + (depth + 1)
        cost = steps * COST[amph]

        new_hallway = list(hallway)
        new_hallway[h_pos] = "."
        new_rooms = [list(r) for r in rooms]
        new_rooms[r_idx][depth] = amph

        yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost

    # Ходы: из комнаты в коридор
    for r_idx in range(4):
        room = rooms[r_idx]
        target_type = ROOM_TYPES[r_idx]

        if all(c == "." or c == target_type for c in room):
            continue

        # Иначе двигаем верхнего присутствующего
        if room[0] != ".":
            depth = 0
            amph = room[0]
        elif room[1] != ".":
            depth = 1
            amph = room[1]
        else:
            continue  # комната пуста

        door = DOOR_POS[r_idx]

        # Идём влево по коридору
        p = door - 1
        while p >= 0:
            if hallway[p] != ".":
                break  # упёрлись в амфипода
            if p in HAL_STOP_POS:
                steps = (depth + 1) + (door - p)
                cost = steps * COST[amph]

                new_hallway = list(hallway)
                new_hallway[p] = amph
                new_rooms = [list(r) for r in rooms]
                new_rooms[r_idx][depth] = "."

                yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost
            p -= 1

        # Идём вправо по коридору
        p = door + 1
        while p < HAL_LEN:
            if hallway[p] != ".":
                break
            if p in HAL_STOP_POS:
                steps = (depth + 1) + (p - door)
                cost = steps * COST[amph]

                new_hallway = list(hallway)
                new_hallway[p] = amph
                new_rooms = [list(r) for r in rooms]
                new_rooms[r_idx][depth] = "."

                yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost
            p += 1


def dijkstra_min_energy(start_state) -> int:
    
    # Поиск минимальной энергии до цели.
    
    goal = goal_state()
    pq = [(0, start_state)]
    best = {start_state: 0}

    while pq:
        cost, state = heapq.heappop(pq)
        if best[state] != cost:
            continue
        if state == goal:
            return cost

        for next_state, move_cost in generate_moves(state):
            new_cost = cost + move_cost
            if next_state not in best or new_cost < best[next_state]:
                best[next_state] = new_cost
                heapq.heappush(pq, (new_cost, next_state))

    return -1  


def solve(lines: list[str]) -> int:
    start_state = parse_input(lines)
    return dijkstra_min_energy(start_state)


def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip("\n"))
    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()