for file in *
do
    file=$(echo "$file" | sed 's/.py$//')
    echo "from $file import $file"
done
