read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 2 3 4 5 6 7 8 10 12 14 15 16 18 20 22
do
for lamb in .2
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method dice_flat --inference_set min_representative --comparison_set rr_2n --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi