read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 5 10 15 20
do
for lamb in .2
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method storm --inference_set min_representative --comparison_set rr_2n --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi