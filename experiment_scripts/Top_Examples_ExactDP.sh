read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 8
do
for lamb in .2
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method dice_flat --inference_set min_representative --comparison_set rr_2n --timeout 900 --get_examples --official
done
done


else
    echo "Never Mind!"
fi