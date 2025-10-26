import sys
import heapq

ROOM_TYPES = "ABCD"
COST = {"A": 1, "B": 10, "C": 100, "D": 1000}
DOOR_POS = [2, 4, 6, 8]        # индексы дверей комнат в коридоре
HAL_LEN = 11
HAL_STOP_POS = {0, 1, 3, 5, 7, 9, 10}  # где можно стоять (не у дверей)


def parse_input(lines: list[str]):
    if len(lines) < 5:
        raise ValueError("Ожидается минимум 5 строк диаграммы")

    corridor = lines[1]
    hallway = tuple(corridor[1:12])  # между стенами

    # Собираем все строки с буквами комнат (между крышкой и дном)
    room_lines = lines[2:-1]
    columns_per_line = []
    for line in room_lines:
        letters = [ch for ch in line if ch in ROOM_TYPES]
        if len(letters) != 4:
            raise ValueError("Неправильный формат комнат")
        columns_per_line.append(letters)

    depth = len(columns_per_line)
    rooms = []
    for r in range(4):
        column = tuple(columns_per_line[k][r] for k in range(depth))
        rooms.append(column)

    return hallway, tuple(rooms)


def goal_state(depth: int):
    hallway = tuple("." for _ in range(HAL_LEN))
    rooms = tuple(tuple(ROOM_TYPES[i] for _ in range(depth)) for i in range(4))
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
    depth = len(rooms[0])

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
        dest_depth = None
        for di in range(depth - 1, -1, -1):
            if room[di] == ".":
                dest_depth = di
                break
        if dest_depth is None:
            continue  # нет места

        steps = abs(h_pos - door) + (dest_depth + 1)
        cost = steps * COST[amph]

        new_hallway = list(hallway)
        new_hallway[h_pos] = "."
        new_rooms = [list(r) for r in rooms]
        new_rooms[r_idx][dest_depth] = amph

        yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost

    # Ходы: из комнаты в коридор
    for r_idx in range(4):
        room = rooms[r_idx]
        target_type = ROOM_TYPES[r_idx]

        # Если в комнате только правильные типы и пустоты, не двигаем
        if all(c == "." or c == target_type for c in room):
            continue

        # Иначе двигаем верхнего присутствующего (самый верхний непустой слот)
        src_depth = None
        amph = None
        for di in range(depth):
            if room[di] != ".":
                src_depth = di
                amph = room[di]
                break
        if amph is None:
            continue  # комната пуста

        door = DOOR_POS[r_idx]

        # Идём влево по коридору
        p = door - 1
        while p >= 0:
            if hallway[p] != ".":
                break  # упёрлись в амфипода
            if p in HAL_STOP_POS:
                steps = (src_depth + 1) + (door - p)
                cost = steps * COST[amph]

                new_hallway = list(hallway)
                new_hallway[p] = amph
                new_rooms = [list(r) for r in rooms]
                new_rooms[r_idx][src_depth] = "."

                yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost
            p -= 1

        # Идём вправо по коридору
        p = door + 1
        while p < HAL_LEN:
            if hallway[p] != ".":
                break
            if p in HAL_STOP_POS:
                steps = (src_depth + 1) + (p - door)
                cost = steps * COST[amph]

                new_hallway = list(hallway)
                new_hallway[p] = amph
                new_rooms = [list(r) for r in rooms]
                new_rooms[r_idx][src_depth] = "."

                yield (tuple(new_hallway), tuple(tuple(r) for r in new_rooms)), cost
            p += 1


def dijkstra_min_energy(start_state) -> int:
    hallway, rooms = start_state
    depth = len(rooms[0])
    goal = goal_state(depth)

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

    return -1  # если цель недостижима (для корректного ввода не должно случиться)


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