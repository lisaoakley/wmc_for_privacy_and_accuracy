read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 2 4 5 6 8 10 12 14 15 16 18 20 22
do
for lamb in .2
do
    ./ExactAcc --mechanism rr_count -n ${n} -l ${lamb} -a 3 --inference_method dice_flat --accuracy_set min_representative --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi