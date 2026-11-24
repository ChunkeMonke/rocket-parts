#!/usr/bin/env bash
# Follow-up: refined-mesh alpha = 0 (zero-force offset of the 2.5M-cell mesh), after the main campaign.
cd "$(dirname "$0")/.."
until grep -q "CAMPAIGN COMPLETE" out/cfd/msp_campaign.log; do sleep 60; done
LOG=out/cfd/msp_campaign.log
n=msp_a0_f
echo "$(date +%T) setup $n --alpha 0 --refine 1" >> $LOG
.venv/bin/python tools/cfd_rocket.py setup --name $n --stl rocket_oml_asm.stl --alpha 0 --speed 100 --refine 1 --iters 1200 >> $LOG 2>&1
sed -i "s/^\(\$MPI foamToVTK -parallel -time '1200' -no-boundary.*\)$/\1 || true/" out/cfd/of_$n/Allrun
bash out/cfd/of_$n/Allrun > out/cfd/of_$n/allrun.out 2>&1
[ -f out/cfd/of_$n/VTKL/rocket/rocket_1200.vtk ] && echo DONE > out/cfd/of_$n/done.flag
.venv/bin/python tools/cfd_post.py --name $n > out/cfd/of_$n/post.out 2>&1
echo "$(date +%T) DONE $n $(grep -h 'Fz_N' out/cfd/of_$n/result.json | tail -1 | tr -d ' \n')" >> $LOG
echo "$(date +%T) FOLLOWUP COMPLETE" >> $LOG
