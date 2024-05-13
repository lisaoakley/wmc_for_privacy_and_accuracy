read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 6
do
for lamb in .05 .1 .15 .2 .25 .3 .35 .4 .45 .5
do
    ./ExactAcc --mechanism rr_count -n ${n} -l ${lamb} -a 3 --inference_method dice_flat --accuracy_set min_representative --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi