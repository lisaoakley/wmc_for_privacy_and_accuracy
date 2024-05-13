read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 2 3 4 5 6
do
for k in 1 2 3
do
for lamb in .2
do
    ./ExactDP --mechanism above_threshold -n ${n} -k ${k} -l ${lamb} -t $((k-1)) --inference_method dice_flat --inference_set exhaustive --comparison_set exhaustive --timeout 900 --official
done
done
done

else
    echo "Never Mind!"
fi