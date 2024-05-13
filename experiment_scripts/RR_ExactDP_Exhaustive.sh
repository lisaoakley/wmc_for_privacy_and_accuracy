read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 2 3 4 5 6 7 8 10 12
do
for lamb in .2
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method dice_flat --inference_set exhaustive --comparison_set exhaustive --timeout 900 --official
done
done

else
    echo "Never Mind!"
fi