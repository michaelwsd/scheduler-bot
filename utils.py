from datetime import datetime, timedelta
from collections import defaultdict
import discord 

events = {}

def get_date_options():
    today = datetime.now()
    return [discord.SelectOption(label=(today + timedelta(days=i)).strftime("%A, %Y-%m-%d")) for i in range(14)]

def get_time_options():
    slots = []
    current = datetime(2000, 1, 1, 9, 0)
    for _ in range(16):  # 16 x 30min slots
        label = current.strftime('%H:%M')
        slots.append(discord.SelectOption(label=label))
        current += timedelta(minutes=30)
    return slots

def get_best_time(events, event_name, interval_minutes=30):
    best_time = None
    best_date = None
    max_users = 0
    best_users = set()

    user_availability = events[event_name]
    date_slot_users = defaultdict(lambda: defaultdict(set))

    for user_id, dates in user_availability.items():
        for date, (start_str, end_str) in dates.items():
            start = datetime.strptime(start_str, "%H:%M")
            end = datetime.strptime(end_str, "%H:%M")

            current = start
            while current < end:
                time_slot = current.strftime("%H:%M")
                date_slot_users[date][time_slot].add(user_id)
                current += timedelta(minutes=interval_minutes)

    # Find the slot with the maximum users
    for date, slot_users in date_slot_users.items():
        for time_str, users_set in slot_users.items():
            if len(users_set) > max_users:
                max_users = len(users_set)
                best_time = time_str
                best_date = date
                best_users = users_set

    del events[event_name]
    
    return best_date, best_time, max_users, best_users

def test():
    test_case_1 = {
        "meeting": {
            1: {"Monday, 2025-07-01": ("09:00", "11:00")},
            2: {"Monday, 2025-07-01": ("09:00", "11:00")},
        }
    }

    best_date, best_time, max_users, users = get_best_time(test_case_1, 'meeting')
    print(f'Best Date: {best_date}\nBest Time: {best_time}\nMax Users: {max_users}\nUsers: {users}')
    print()

    test_case_2 = {
        "meeting": {
            1: {"Tuesday, 2025-07-02": ("09:00", "10:00")},
            2: {"Tuesday, 2025-07-02": ("09:30", "11:00")},
        }
    }

    best_date, best_time, max_users, users = get_best_time(test_case_2, 'meeting')
    print(f'Best Date: {best_date}\nBest Time: {best_time}\nMax Users: {max_users}\nUsers: {users}')
    print()

    test_case_3 = {
        "meeting": {
            1: {"Wednesday, 2025-07-03": ("09:00", "10:00")},
            2: {"Wednesday, 2025-07-03": ("10:00", "11:00")},
        }
    }

    best_date, best_time, max_users, users = get_best_time(test_case_3, 'meeting')
    print(f'Best Date: {best_date}\nBest Time: {best_time}\nMax Users: {max_users}\nUsers: {users}')
    print()


if __name__ == "__main__":
    test()