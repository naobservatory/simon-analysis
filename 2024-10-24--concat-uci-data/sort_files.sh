# Add header to the output file

echo -e "date\tfile" > fwd_read_files.tsv

for delivery in $(aws s3 ls s3://nao-restricted/ | awk '{print $NF}' | grep ^JR | sed 's~/$~~') ; do
    cat ~/code/mgs-restricted/dashboard/$delivery.metadata.tsv | grep -v sample | grep -v NotRecog | awk -F '\t' '{print $4"\t'$delivery'\ts3://nao-restricted/'$delivery'/raw/"$1}';
done | sort | while read date delivery prefix ; do
    aws s3 ls $prefix | awk '{print $NF}' | grep _1.fastq.gz | xargs -I {} echo -e "$date\t$(dirname $prefix)/{}" ;
done >> fwd_read_files.tsv
