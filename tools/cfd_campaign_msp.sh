#!/usr/bin/env bash
# CFD campaign for the Ms. Piggy assembly OML (out/cfd/rocket_oml_asm.stl). Sequential, 4 cores.
#   bash tools/cfd_campaign_msp.sh  -> out/cfd/of_msp_*/ ; progress in out/cfd/msp_campaign.log
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
LOG=out/cfd/msp_campaign.log
run() {  # name, setup args...
  local n=$1; shift
  if [ -f out/cfd/of_$n/done.flag ]; then echo "$(date +%T) skip $n (done)" >> $LOG; return; fi
  echo "$(date +%T) setup $n $*" >> $LOG
  $PY tools/cfd_rocket.py setup --name $n --stl rocket_oml_asm.stl "$@" >> $LOG 2>&1 || { echo "$(date +%T) SETUP FAILED $n" >> $LOG; return; }
  bash out/cfd/of_$n/Allrun > out/cfd/of_$n/allrun.out 2>&1
  if [ -f out/cfd/of_$n/done.flag ]; then
    $PY tools/cfd_post.py --name $n > out/cfd/of_$n/post.out 2>&1
    echo "$(date +%T) DONE $n $(grep -h -m1 'CP_from_tip_mm' out/cfd/of_$n/result.json | tr -d ' \n') $(grep -h 'CN_alpha_per_rad' out/cfd/of_$n/result.json | tail -1 | tr -d ' \n')" >> $LOG
  else
    echo "$(date +%T) RUN FAILED $n" >> $LOG
  fi
}
run msp_a4    --alpha 4 --speed 100
run msp_a4_f  --alpha 4 --speed 100 --refine 1 --iters 1200
run msp_a0    --alpha 0 --speed 100
run msp_a2    --alpha 2 --speed 100
run msp_a6    --alpha 6 --speed 100
run msp_a8    --alpha 8 --speed 100
run msp_m05   --alpha 4 --mach 0.5
run msp_m08   --alpha 4 --mach 0.8
echo "$(date +%T) CAMPAIGN COMPLETE" >> $LOG
