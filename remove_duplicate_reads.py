import argparse

def is_fastq(file_path):
    with open(file_path, 'r') as file:
        first_char = file.read(1)
        return first_char == '@'

def is_fasta(file_path):
    with open(file_path, 'r') as file:
        first_char = file.read(1)
        return first_char == '>'


def remove_duplicate_reads(fastx_file, output_file):
    is_fastq_file = is_fastq(fastx_file)
    is_fasta_file = is_fasta(fastx_file)

    sequences = {}

    with open(fastx_file, 'r') as file:
        if is_fastq_file:
            lines = file.readlines()
            for i in range(0, len(lines), 4):
                read_id = lines[i].strip()[1:]  
                read_seq = lines[i+1].strip()
                read_qual = lines[i+3].strip()

                if read_seq not in sequences:
                    sequences.setdefault(read_seq, []).append((read_id, read_seq, read_qual))
        elif is_fasta_file:
            read_id = ""
            read_seq = ""

            for line in file:
                line = line.strip()

                if line.startswith('>'):
                    if read_id and read_seq not in sequences:
                        sequences.setdefault(read_seq, []).append((read_id, read_seq, None))
                    read_id = line[1:]
                    read_seq = ""
                else:
                    read_seq += line

            if read_id and read_seq not in sequences:
                sequences.setdefault(read_seq, []).append((read_id, read_seq, None))

    sorted_sequences = sorted(sequences.values())

    with open(output_file, 'w') as file:
        if is_fastq_file:
            for sequence_data in sorted_sequences:
                for sequence_id, sequence, qual in sequence_data:
                    file.write('@' + sequence_id + '\n')
                    file.write(sequence + '\n')
                    file.write('+\n')
                    file.write(qual + '\n')
        elif is_fasta_file:
            for sequence_data in sorted_sequences:
                for sequence_id, sequence, _ in sequence_data:
                    file.write('>' + sequence_id + '\n')
                    file.write(sequence + '\n')


def count_reads(fastx_file):
    count = 0
    with open(fastx_file, 'r') as f:
        for line in f:
            if line.startswith('@') or line.startswith('>'):
                count += 1
    return count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove duplicate reads.')
    parser.add_argument('-i', '--input', metavar='input.fastx', help='input FASTA or FASTQ file')
    parser.add_argument('-o', '--output', metavar='output.fastx', help='output FASTA or FASTQ file')

    args = parser.parse_args()

    if not args.input or not args.output:
        parser.print_help()
    else:
        input_file = args.input
        output_file = args.output
        count_before = count_reads(input_file)
        remove_duplicate_reads(input_file, output_file)
        count_after = count_reads(output_file)
        print("Reads before removing duplicate reads:", count_before)
        print("Reads after removing duplicate reads:", count_after)
