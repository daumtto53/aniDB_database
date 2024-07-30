import os

def divide_file_by_8000_lines() :
    lines = []
    with open('../resources/mangaupdates/manga_link.txt', 'r') as f:
        lines = f.read().split('\n')
        print(len(lines))

    batch = int(len(lines) / 8000) + 1
    for i in range(batch):
        with open(f'../resources/mangaupdates/manga_link_batch_{i}.txt', 'w') as f:
            for j in range(8000):
                f.write(lines[i*8000 + j])
                f.write('\n')









divide_file_by_8000_lines()
