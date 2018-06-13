import collections


def count_num_seq(vcf_file):
    """
    This function calculates the number of sequences in the VCF file
    :param vcf_file: a VCF file
    :return: a number. Number of sequences in the VCF file. For now, assume the species
    is diploid.
    """
    num_seq = 0
    with open(vcf_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#CHROM'): #remove #
                line = line.split('\t')
                num_seq = (len(line[9:]))*2
                break
    return num_seq


def count_alt_allele(vcf_file):
    """
    This function calculates the number of alternate alleles for each variant.

    :param vcf_file: a VCF file
    :return: a list where each item in the list is the count of the alternate allele
    for each variant
    """
    alt_allele_count = []
    with open(vcf_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.startswith('#'): #remove #
                line = line.split('\t')
                count = 0
                for i in range(9, len(line)):
                    genotype = line[i]
                    if genotype == '0|1' or genotype == '1|0' or genotype == '0/1' \
                            or genotype == '1/0':
                        count += 1
                    if genotype == '1|1' or genotype == '1/1':
                        count += 2
                alt_allele_count.append(count)
    return alt_allele_count


def make_sfs(num_seq, alt_allele_count):
    """
    This function makes a site frequency spectrum following equation 1.2 in John Wakely's
    Coalescent book.

    :param num_seq: number of sequences in the VCF file.
    :param alt_allele_count: a list where each item in the list is the count of the
    alternate alleles for each variant
    :return: a dictionary where keys are frequency and values are the count of variants
    at that frequency
    """

    # frequency_count is a dictionary where keys indicate the frequency and values
    # indicate how many variants there are at that particular frequency.
    frequency_count = collections.Counter(alt_allele_count)

    # Generate a folded site frequency spectrum
    sfs = {}
    for i in range(1, (num_seq / 2) + 1):
        if i != (num_seq - i):
            count = float(frequency_count[i] + frequency_count[num_seq - i])
            sfs[i] = int(count)
        else:
            count = float(frequency_count[i] + frequency_count[num_seq - i]) / 2
            sfs[i] = int(count)
    return sfs


def compute_af(vcf_file, num_seq):
    """
    This function computes the allele frequency for each variant

    :param vcf_file: a VCF file
    :param num_seq: number of chromosome in the VCF file
    :return: a dictionary where key is the position of the variant and value is the
    allele frequency of that variant
    """
    variants_af = {}
    with open(vcf_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.startswith('#'):
                line = line.split('\t')
                count = 0
                for i in range(9, len(line)):
                    genotype = line[i]
                    if genotype == '0|1' or genotype == '1|0' or genotype == '0/1' or genotype == '1/0':
                        count += 1
                    if genotype == '1|1' or genotype == '1/1':
                        count += 2
                variants_af[int(line[1])] = float(count)/num_seq
    return variants_af


def compute_pi(window_file, variants_af, num_seq):
    """
    This function computes pi in each nonoverlapping window

    :param window_file: a BED file specifying the coordinates for each nonoverlapping window
    :param variants_af: a dictionary where key is the position of the variant and value
    is the allele frequency of that variant. This is the output from the function compute_af.
    :param num_seq: number of sequences in the VCF file
    :return: a dictionary where key is the (start, end) coordinates and value is pi for that window.
    """
    windows_pi = {}
    with open(window_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            line = line.split('\t')
            start = int(line[1])
            end = int(line[2])
            total_pi = 0
            for variant in variants_af.keys():
                if start <= variant and variant < end:
                    af = variants_af[variant]
                    pi = 2* af * (1-af)
                    total_pi += pi
            total_pi_adjusted = (num_seq/(num_seq-1))*total_pi

            windows_pi[(start, end)] = total_pi_adjusted
    return windows_pi

