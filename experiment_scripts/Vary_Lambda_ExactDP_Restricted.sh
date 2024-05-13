read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 6
do
for lamb in .05 .1 .15 .2 .25 .3 .35 .4 .45 .5
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method dice_flat --inference_set min_representative --comparison_set rr_2n --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi