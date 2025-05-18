from collections import deque
import random
import matplotlib.pyplot as plt
from tabulate import tabulate

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid  # Process ID
        self.arrival = arrival
        self.burst = burst  # Service time
        self.remaining = burst  # Remaining service time
        self.waiting = 0
        self.turnaround = 0
        self.completion = 0     # Finish time

def round_robin(processes, quantum):
    time = 0    # Current time
    queue = deque()
    # sort process by arrival time
    remaining_processes = sorted(processes, key=lambda p: p.arrival)


    while remaining_processes or queue:
        # Add processes that have arrived by the current time to the queue
        while remaining_processes and remaining_processes[0].arrival <= time:
            queue.append(remaining_processes.pop(0))

        if queue:
            # FIFO: Get the next process from the queue
            process = queue.popleft()
            # If remaining time is less than quantum, the process will finish after this execution
            # If quantum is less than remaining time, the process will not finish after this execution
            execution = min(process.remaining, quantum)
            time += execution
            process.remaining -= execution

            print(f'Time {time - execution}-{time}: P{process.pid} runs for {execution} units (remaining burst time = {process.remaining}).')

            if process.remaining == 0:
                process.completion = time   # Set completion time
                process.turnaround = time - process.arrival     # Calculate turnaround time
                process.waiting = process.turnaround - process.burst    # Calculate waiting time
                print(f'P{process.pid} finishes execution.')
            else:
                # Add newly arrived processes to the queue
                while remaining_processes and remaining_processes[0].arrival <= time:
                    queue.append(remaining_processes.pop(0))
                queue.append(process)   # Re-add the current process to the queue
        else:
            # Increment time if no process is in the queue
            time += 1

    print_process_table(processes)

    return processes

def adaptive_round_robin(processes, initial_quantum):
    time = 0        # Current time
    queue = deque()
    in_queue = set()       # Set to track processes in the queue
    round_number = 1
    quantum = initial_quantum
    # Sort processes by arrival time
    remaining_processes = sorted(processes, key=lambda p: p.arrival)

    while remaining_processes or queue:
        # Add processes that have arrived by current time and not in queue
        while remaining_processes and remaining_processes[0].arrival <= time:
            process = remaining_processes.pop(0)
            queue.append(process)
            in_queue.add(process.pid)

        if not queue:
            # Check if all processes are done
            remaining = sum(1 for p in processes if p.remaining > 0)
            if remaining == 0:
                break

            next_arrivals = [p.arrival for p in processes if p.remaining > 0]
            if not next_arrivals:
                break
            next_arrival = min(next_arrivals)
            time = next_arrival
            continue

        print(f'Round {round_number} (Quantum = {quantum})')
        completed = False
        initial_queue_length = len(queue)

        for _ in range(initial_queue_length):
            process = queue.popleft()
            in_queue.remove(process.pid)

            start_time = max(time, process.arrival)
            execution = min(process.remaining, quantum)
            end_time = start_time + execution
            time = end_time
            process.remaining -= execution

            # Add newly arrived processes after time update (before moving to next process in the round)
            while remaining_processes and remaining_processes[0].arrival <= time:
                new_process = remaining_processes.pop(0)
                queue.append(new_process)
                in_queue.add(new_process.pid)

            print(f'Time {start_time}-{end_time}: P{process.pid} runs for {execution} units (remaining burst time = {process.remaining}).')

            if process.remaining == 0:
                process.completion = end_time       # Set finish time
                process.turnaround = end_time - process.arrival         # Calculate turnaround time
                process.waiting = process.turnaround - process.burst    # Calculate waiting time
                completed = True
                print(f'P{process.pid} finishes execution.')
            else:
                queue.append(process)   # Re-add the current process to the queue
                in_queue.add(process.pid)

        if completed:
            quantum = max(1, quantum - 1)   # Decrease quantum if a process was completed
            print(f'End of Round {round_number}: Quantum decreases to {quantum}.')
        else:
            quantum += 1       # Increase quantum if no process was completed
            print(f'End of Round {round_number}: Quantum increases to {quantum}.')

        round_number += 1
        print()
    print_process_table(processes)
    return processes

def calculate_metrics(processes):
    mean_waiting = sum(p.waiting for p in processes) / len(processes)      # Calculate mean waiting time
    mean_turnaround = sum(p.turnaround for p in processes) / len(processes)  # Calculate mean turnaround time
    return mean_waiting, mean_turnaround


def plot_results(rr_results, adaptive_results, title, ylabel):
    labels = [f'RR {q}' for q in rr_results.keys()] + [f'Adaptive {q}' for q in adaptive_results.keys()]
    values = list(rr_results.values()) + list(adaptive_results.values())

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(labels, values, color=['#4C72B0'] * len(rr_results) + ['#55A868'] * len(adaptive_results))

    avg_rr = sum(rr_results.values()) / len(rr_results)
    avg_adaptive = sum(adaptive_results.values()) / len(adaptive_results)
    ax.axhline(avg_rr, color='#4C72B0', linestyle='--', label=f'RR Avg: {avg_rr:.2f}')
    ax.axhline(avg_adaptive, color='#55A868', linestyle='--', label=f'Adaptive Avg: {avg_adaptive:.2f}')

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()

    plt.xticks(rotation=50)
    plt.tight_layout()
    plt.show()

def generate_processes(n):
    processes = []
    for i in range(n):
        arrival_time = random.randint(0, 100)       # Random arrival time
        burst_time = random.randint(10, 30)       # Random burst time
        processes.append(Process(i, arrival_time, burst_time))
    return processes


def print_process_table(processes):
    table_data = [
        [p.pid, p.arrival, p.burst,p.completion ,p.waiting, p.turnaround]
        for p in processes
    ]

    headers = ["PID", "Arrival Time", "Burst Time","Finish Time" ,"Waiting Time", "Turnaround Time"]

    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", numalign="center"))
    print()

def main():
    processes = generate_processes(5)       # Generate random processes
    # processes = [Process(0, 13, 12),
    #              Process(1, 3, 11),
    #              Process(2, 98, 18),
    #              Process(3, 75, 20),
    #              Process(4, 71, 27)
    #              ]
    # processes = [Process(1, 0, 16),
    #              Process(2, 0, 8),
    #              Process(3, 0, 12),
    #              Process(4, 0, 10)]

    # processes = [Process(0, 34, 24),
    #              Process(1, 97, 13),
    #              Process(2, 78, 15),
    #              Process(3, 21, 13),
    #              Process(4, 64, 13)]

    rr_waiting = {}
    rr_turnaround = {}
    for quantum in [2,3,4,5]:
        print(f'Running Round Robin with Quantum = {quantum}')
        rr_procs = [Process(p.pid, p.arrival, p.burst) for p in processes]
        round_robin(rr_procs, quantum)
        wait, turnaround = calculate_metrics(rr_procs)
        rr_waiting[quantum] = wait
        rr_turnaround[quantum] = turnaround
        print(f'Round Robin(q = {quantum}): Mean Waiting Time = {wait:.2f}, Mean Turnaround Time = {turnaround:.2f}')
        print('------------------')


    print('Adapted Round Robin\n')
    adaptive_waiting = {}
    adaptive_turnaround = {}
    adaptive_procs = [Process(p.pid, p.arrival, p.burst) for p in processes]
    adaptive_round_robin(adaptive_procs, 4)

    wait, turnaround = calculate_metrics(adaptive_procs)
    adaptive_waiting[quantum] = wait
    adaptive_turnaround[quantum] = turnaround
    print(f'Adaptive Round Robin: Mean Waiting Time = {wait:.2f}, Mean Turnaround Time = {turnaround:.2f}')

    # Plot waiting time
    plot_results(rr_waiting, adaptive_waiting, "Comparison of Waiting Time", "Average Waiting Time")

    # Plot turnaround time
    plot_results(rr_turnaround, adaptive_turnaround, "Comparison of Turnaround Time", "Average Turnaround Time")


if __name__ == '__main__':
    main()
