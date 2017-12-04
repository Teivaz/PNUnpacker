Classes2 = {}

Classes = {
	'n3dnode': {
		'QXYZ': ('ffff', '_QXYZ'),
		'SBLB': ('b', '_SBLB'),
		'SHDT': ('b', '_SHDT'),
		'SLVW': ('b', '_SLVW'),
		'SMLD': ('f', '_SMLD'),
		'SVWS': ('b', '_SVWS'),
		'RXYZ': ('fff', 'rotate_xyz'),
		'SACT': ('b', '_SACT'),
		'SFAF': ('f', 'setfinishedafter'),
		'SSPR': ('b', '_SSPR'),
		'SXYZ': ('fff', 'scale_xyz'),
		'TXYZ': ('fff', 'translate_xyz'),
	},
	'nflipflop': {
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'AKEY': ('fs', 'add_key'),
	},
	'nmeshipol': {
		'SKEY': ('ifs', 'setkey'),
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SRDO': ('b', '_SRDO'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SUCD': ('b', '_SUCD'),
		'SUCL': ('b', '_SUCL'),
	},
	'nchnsplitter': {
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SKEY': ('ifs', 'setkey'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
	},
	'nlinknode': {
		'STGT': ('o', 'settarget'),
	},
	'nmeshnode': {
		'SKEY': ('iffffff', 'setkey'),
		'SFLN': ('s', 'setfilename'),
		'SRDO': ('b', '_SRDO'),
		'SCSD': ('b', '_SCSD'),
	},
	'nparticlesystem': {
		'SLFT': ('f', 'setlifetime'),
		'SFRQ': ('f', 'setfreq'),
		'SSPD': ('f', 'setspeed'),
		'SACC': ('fff', 'setaccel'),
		'SICN': ('f', 'setinnercone'),
		'SOCN': ('f', 'setoutercone'),
		'SSPN': ('f', 'setspin'),
		'SSPA': ('f', 'setspinaccel'),
		'SEMT': ('s', 'setemmiter'),
	},
	'njointanim': {
		'BGJN': ('i', 'beginjoints'),
		'EDJN': ('v', 'endjoints'),
		'ADJN': ('isifffffff', 'addjoint'),
		'BGST': ('i', 'beginstates'),
		'ADST': ('is', 'addstate'),
		'BGSA': ('ii', 'beginstateanims'),
		'ADSA': ('iis', 'addstateanim'),
		'EDSA': ('i', 'endstateanims'),
		'EDST': ('v', 'endstates'),
		'BGHP': ('i', 'beginhardpoints'),
		'ADHP': ('iis', 'addhardpoint'),
		'EDHP': ('v', 'endhardpoints'),
	},
	'nipol': {
		'SK1F': ('iff', 'setkeys1f'),
		'SK2F': ('ifff', 'setkeys2f'),
		'SK3F': ('iffff', 'setkeys3f'),
		'SK4F': ('ifffff', 'setkeys4f'),
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'CNCT': ('s', 'connect'),
		'SSCL': ('f', 'setscale'),
		'BGKS': ('ii', 'beginkeys'),
		'ENKS': ('v', 'endkeys'),
		'SIPT': ('s', '_SIPT'),
	},
	'nchnmodulator': {
		'BGIN': ('i', 'begin'),
		'SET_': ('iss', 'set'),
		'END_': ('v', 'end'),
	},
	'nhousemenu': {
		'SMRD': ('f', '_SMRD'),
		'STAD': ('f', '_STAD'),
		'SISP': ('f', '_SISP'),
		'SIDS': ('f', '_SIDS'),
	},
	'ncloud': {
		'BCDS': ('if', '_BCDS'),
		'SLNF': ('f', '_SLNF'),
		'ECDS': ('v', 'enableclouds'),
	},
	'nmissileengine3': {
		'SIDL': ('f', '_SIDL'),
		'SGVF': ('f', '_SGVF'),
		'SMXS': ('f', '_SMXS'),
		'SAGL': ('f', '_SAGL'),
	},
	'nmeshcluster2': {
		'SSMS': ('s', '_SSMS'),
		'SCTS': ('b', '_SCTS'),
		'SRTJ': ('s', '_SRTJ'),
		'SRDO': ('b', '_SRDO'),
	},
	'ncurvearraynode': { #nipol
		'BGCN': ('i', 'beginconnects'),
		'EDCN': ('v', 'endconnects'),
		'SCHN': ('s', 'setchannel'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SFLN': ('s', 'setfilename'),
		'EDBD': ('v', '_EDBD'),
		'SBC2': ('iss', '_SBC2'),
		'BGBD': ('is', '_BGBD'),
		'BGCB': ('i', '_BGCB'),
		'SCBD': ('iss', '_SCBD'),
		'EBCB': ('v', '_EBCB'),
		'SCC2': ('iss', '_SCBD'),
	},
	'nweighttree': {
		'ANOD': ('sss', 'addnode'),
		'ALEF': ('s', 'addleaf'),
	},
	'ncharacternode': { # njointanim, nchsplitter, nmeshnode
		'EDSA': ('i', 'endstateanims'),
		'BGHP': ('i', 'beginhardpoints'),
		'BGSA': ('ii', 'beginstateanims'),
		'BGJN': ('i', 'beginjoints'),
		'SSKM': ('s', '_SSKM'),
		'SRPT': ('s', 'setreptype'),
		'EDHP': ('v', 'endhardpoints'),
		'ADSA': ('iis', 'addstateanim'),
		'SRDO': ('b', '_SRDO'),
		'EDJN': ('v', 'endjoints'),
		'ADJN': ('isifffffff', 'addjoint'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'ADHP': ('iis', 'addhardpoint'),
		'SSTC': ('s', '_SSTC'),
		'EDST': ('v', 'endstates'),
		'SANF': ('s', '_SANF'),
		'BGST': ('i', 'beginstates'),
		'SCSS': ('b', '_SCSS'),
		'ADST': ('is', 'addstate'),
	},
	'nanimsequence': {
		'ADTK': ('ffff', '_ADTK'),
		'ADQK': ('fffff', '_ADQK'),
		'STIT': ('i', '?STIT'),
		'SVRL': ('b', '_SVRL'),
		'ADVK': ('fs', '_ADVK'),
		'ADAK': ('fs', '_ADAK'),
		'ADRK': ('ffff', '_ADRK'),
	},
	'ntrailrender': {
		'SKEY': ('iffffff', 'setkey'),
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SEMT': ('s', 'setemmiter'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SSPA': ('f', 'setspinaccel'),
		'SSPN': ('f', 'setspin'),
		'SSTR': ('b', '_SSTR'),
	},
	'nspriterender': {
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'SSPN': ('f', 'setspin'),
		'SSPA': ('f', 'setspinaccel'),
		'SEMT': ('s', 'setemmiter'),
		'BKEY': ('i', 'beginkeys'),
		'SKEY': ('iffffff', 'setkey'),
		'EKEY': ('v', 'endkeys'),
		'SSTR': ('b', '_SSTR'),
	},
	'nmeshemitter': { # nparticlesystem
		'SACC': ('fff', 'setaccel'),
		'SOCN': ('f', 'setoutercone'),
		'SCHN': ('s', 'setchannel'),
		'SRPT': ('s', 'setreptype'),
		'SICN': ('f', 'setinnercone'),
		'SSCL': ('f', 'setscale'),
		'SSPD': ('f', 'setspeed'),
		'STMS': ('fff', '_STMS'),
		'SMSN': ('s', '_SMSN'),
		'SFRQ': ('f', 'setfreq'),
		'SLFT': ('f', 'setlifetime'),
	},
	'nshadernode': {
		'SMMF': ('s', 'set_min_max_filter'),
		'SEMV': ('fff', '_SEMV'),
		'SPOP': ('i', '_SPOP'),
		'SADR': ('s', 'set_ADR'),
		'SABL': ('s', 'set_alpha_blending'),
		'SZFC': ('s', 'set_ZFC'),
		'SCMD': ('s', 'set_CMD'),
		'SCLM': ('s', 'set_CLM'),
		'SAFC': ('s', 'set_AFC'),
		'SAOP': ('is', 'set_AOP'),
		'SDIF': ('ffff', 'set_diffuse_color'),
		'SAMB': ('ffff', 'set_ambient_color'),
		'SCOT': ('iiiii', '_SCOT'),
		'SLEN': ('b', 'set_LEN'),
		'SAEN': ('b', 'set_AEN'),
		'SZEN': ('b', 'set_ZEN'),
		'SFEN': ('b', 'set_FEN'),
		'SATE': ('b', 'set_ATE'),
		'SENT': ('b', '_SENT'),
		'SMLB': ('i', '_SMLB'),
		'SNST': ('i', '_SNST'),
		'BGTU': ('i', '_BGTU'),
		'SARF': ('f', '_SARF'),
		'SRPR': ('i', '_SRPR'),
		'EDTU': ('v', 'enable_DTU'),
		'STCS': ('s', 'set_TCS'),
		'TXYZ': ('fff', 'translate_xyz'),
		'RXYZ': ('fff', 'rotate_xyz'),
		'SXYZ': ('fff', 'scale_xyz'),
	},
	'nairplane3': {
		'SATM': ('f', '_SATM'),
		'SDTM': ('f', '_SDTM'),
		'SISP': ('f', '_SISP'),
		'SMPI': ('f', '_SMPI'),	
		'SMPT': ('f', '_SMPT'),
		'SMRL': ('f', '_SMRL'),
		'SMRT': ('f', '_SMRT'),
		'SXSP': ('f', '_SXSP'),
		'SXYR': ('f', '_SXYR'),
		'SYAT': ('f', '_SYAT'),
	},
	'nbuildartefact': {
		'SBEN': ('f', '_SBEN'),
		'SBPR': ('s', '_SBPR'),
		'SBTM': ('f', '_SBTM'),
		'SBRP': ('iff', '?SBRP'),
		'SMPR': ('i', '_SMPR'),
		'SSID': ('i', '_SSID'),
	},
	######################################

		#'BGKS': ('ii', 'beginkeys'),
		#'ENKS': ('v', 'endkeys'),

		#'SK1F': ('iff', 'setkey1f'),
		#'CNCT': ('s', 'connect'),
	'nairship3':{},
	'nartefactstorage':{},
	'nartefacttransformer':{},
	'nattack':{},
	'navoidcollision':{},
	'nbombard':{},
	'nbomber':{},
	'nbuildflak':{},
	'nbuildtradeartefact':{},
	'nbuildvehicle':{},
	'ncharaudio':{},
	'nchnreader':{},
	'ncinedummy':{},
	'nclouddesc':{},
	'ncloudrender':{},
	'nclouds':{},
	'ncollectartefact':{},
	'ncollectore':{},
	'ncollhandle2':{},
	'nconsumption':{},
	'ncontainer':{},
	'ncritter2':{},
	'ncrittercollhandle':{},
	'ncritterdamage':{},
	'ncritterengine2':{},
	'nenergycollector':{},
	'nexplosion':{},
	'nfactory':{},
	'nfiremachinegun':{},
	'nfiremissile':{},
	'nflak':{},
	'nflakengine2':{},
	'nfognode':{},
	'nfreesteer':{},
	'ngarage':{},
	'ngrassrender':{},
	'nheal':{},
	'nhouse':{},
	'nhypermixer2':{},
	'nipolapproachgarage':{},
	'nislanddrive':{},
	'njoint2':{},
	'nleafrender':{},
	'nlenseflare':{},
	'nlightnode':{},
	'nlistenernode':{},
	'nmaennel':{},
	'nmaennelengine3':{},
	'nmaennelwalk2':{},
	'nmeshipol':{},
	'nmeshmixer':{},
	'nmeshsway':{},
	'nmgrender':{},
	'nmissile':{},
	'nmissilecollcheck':{},
	'nmissileengine2':{},
	'nmixer':{},
	'nmnlcollhandle2':{},
	'nmodartefact':{},
	'nnavpoint':{},
	'nnavpointsteer':{},
	'nore':{},
	'npawnshop':{},
	'nplacehouse':{},
	'nplacespellaction':{},
	'npointemitter':{},
	'npowersupply':{},
	'nreplenish':{},
	'nsammler':{},
	'nshadowcontrol':{},
	'nsilo':{},
	'nsoundnode':{},
	'nspawnpoint':{},
	'nsquadronwatchtarget':{},
	'nstandardmenu':{},
	'nstatewatch':{},
	'nstaticmeshemitter':{},
	'nstation':{},
	'nstationengine3':{},
	'nstoragemenu':{},
	'nsubtitle':{},
	'nswimmingengine':{},
	'nswingengine':{},
	'ntestpossess':{},
	'ntexarraynode':{},
	'nthreshnode':{},
	'ntrademenu':{},
	'ntransformmenu':{},
	'ntriggerobject':{},
	'nunloadore':{},
	'nvehicle':{},
	'nvehicleemitter':{},
	'nviewerdata':{},
	'nvisual':{},
	'nwalkcollhandle2':{},
	'nwatchtarget':{},
	'nweatherdesc':{},

}
