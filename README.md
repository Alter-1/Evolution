# Evolution simulation

World.py - engine
LifeEmu.py - UI
RtspFrame.py - visualization

Run evolution process in society of monogamous species.

	Windows
	
start-life.cmd   - run script for Windows
start-life_c.cmd - run precompiled (cythonized) version, should be faster. Use '_c_build.sh' to build it
'_c_build.bat'   - build precompiled (cythonized) version

	Linux

start-life.sh   - run script for Lunux
start-life_c.sh - run precompiled (cythonized) version, should be faster. Use '_c_build.sh' to build it
'_c_build.sh'   - build precompiled (cythonized) version

	GUI World Settings

iq0 - start new world with zero skills, if not set, world with random creatures would be created
local res - allow creatures to get 1 point of energy from ts location unconditionally

	In-source World Settings

open World.py and change global options there, then run with 'start-life' or recompile with 

	There are the following 'genes':

share (altruism) - help others with energy for free
aggressive       - skill of taking energy from others without permission (attack)
iq               - IQ, improves efficiency of 
                    extracting energy from outer space and from inventions,
                    learning rate (rate of experience growth)
                    attacks and defence
defence          - resistance to attacks
mobility         - max distance for movements and getting energy and choice between free space requirement and finding pair
fert             - fertility

	There are following run-time states:

energy           - energy, used for life 91 per cycle), giving birth and feeding children
age              -
sex              - male/female
exp              - experience, works like IQ, but is accumulated during life time of creature
                    Experience growth rate and efficiency of passing experience from parents depends on IQ

	Process Stages

1 - check energy and age of creatures. Creature dies when enery level reaches 0 or age reaches limit
2 - get energy from outer space or invent something
3 - try find 'better place'. Either creature of different sex or free place with less neibghors
4 - female creatures look up for males and create children. It is expensive process since females pass some energy to children.
    males may compensate part of energy depending on 'share' gene

