#!/bin/bash
#
# Bash script for evaluating the cosine similarity of every document with every
# 	other document in a directory.

if $# < 1 
then
	echo "Need index for the search"
	exit 1
fi

if $# < 2
then
	echo "Need path to the directory that contains files"
	exit 1
fi

suma=0
max=0
maxFich=""
min=1
minFich=""
numElem=0

for file in $2/*
do
	for file2 in $2/*
	do
		if [ $file = $file2 ]
		then
			continue
		fi

		aux=$(python3 TFIDFViewer.py --index $1 --files $file $file2 2>/dev/null | cut -c 14-20 | bc)

		suma=$( echo $suma + $aux | bc)
		numElem=$(echo $numElem + 1 | bc)

		if [ $(bc <<< "$max < $aux") -eq 1 ]
		then
			max=$aux
			maxFich=$(echo $file $file2)
		fi
		if [ $(bc <<< "$min > $aux") -eq 1 ]
		then
			min=$aux
			minFich=$(echo $file $file2)
		fi
	done
done

echo $suma
suma=$(bc <<< "$suma / $numElem")

echo "The sum of all similarities is : " $suma " for " $numElem " pairs of documents"
echo "The max similarity is  : " $max " between " $maxFich 
echo "The min similarity is  : " $min " between " $minFich
