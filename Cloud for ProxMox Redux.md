# Cloud for ProxMox

This is a second attempt at creating a Cloud Service Provider management solution, build on top of ProxMox.

* an earlier effort can be found here: https://github.com/peppekerstens/cloudforproxmox-old
* GUI and functionality wise, everything went fine up until a certain point
* that point is very likely this commit: https://github.com/peppekerstens/cloudforproxmox-old/commit/040259b6772556d4c94b93b6aa404d0de98791a3
* beyond this commit, effort were started enable https and to separate back-end and front-end fysically over two lxc instances
* the redeployment of the database failed and the old one was deleted.
* AI spend that time until now to repair but no working solution as of yet

## AI experiences and pitfalls

* Despite very specific instructions, AI repeatedly forgets critical rules and requirements
* When not being very clear AI seems to do different things than you expect. So 'check github' is different then 'check github issues'. Also single words are fast but also provide room for interpretation and may be deduced as something different. As a result, next point.
* AI seems impatient itself; when something takes longer than expected, it 'just decides' a different path to move forward, not always being clear we strayed from the plan.

## Lessons learned

* as it turns out, using an LXC as a docker host was the wrong choice. it simply does not work. this is documented in the internet. an VM with docker on top works. this should be described well on current state of ttps://github.com/peppekerstens/cloudforproxmox-old
* more gates and/or insurances are required during development to ENSURE (re)deployment of the solution or when to revert to a working state to properly analyze the discrepancies from written instructions/code and reality. think of:
  * backup or snapshot from complete VM. the name of the snapshot should contain the commit. rotate/replace rule which ENSURES a history of at least 2 working scanarios
  * on major changes like phase or epic, test a complete deployment on another temporary VM FIRST and confirm all tests work. THEN deploy on actual development VM. test again on actual development VM. THEN destroy the temporary VM
  * document a working scenario in the documentation of the repo, use hash- and/or permalinks to pinpoint to exact commit of working scenario
* ALWAYS plan first. reassess often.

## The idea

* to start, upload this repo to https://github.com/peppekerstens and keep it private
* derive from https://github.com/peppekerstens/cloudforproxmox-old all rules and settings for AI development via opencode
* critically assess those rules and settings, suggest a best-practice implementation into this repo. ENSURE that lessons learned of this file are being merged-in
* the idea is to just start-over. so taking the very first commit of https://github.com/peppekerstens/cloudforproxmox-old as input and then replaying up until https://github.com/peppekerstens/cloudforproxmox-old/commit/040259b6772556d4c94b93b6aa404d0de98791a3
* no smart thinking. no replanning
* a few exceptions and contraints:
   * create a clean dev machine based on latest findings in https://github.com/peppekerstens/cloudforproxmox-old 
   * ONLY the changes made to code and repeat them, both in this repo and on the dev machine in such a way that we can actually do REAL testing
   * once arrived, we will re-assess the actual state of code and dev machine and compare with ALL what has been documented in ttps://github.com/peppekerstens/cloudforproxmox-old
