read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then


for n in 2 4 6
do
for lamb in .2
do
    ./ExactDP --mechanism rr -n ${n} -l ${lamb} --inference_method storm --inference_set exhaustive --comparison_set exhaustive --timeout 900 --official
done
done


else
    echo "Never Mind!"
fi
