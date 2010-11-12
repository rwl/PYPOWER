function mptest
casenames = {'case118' 'case2383wp' 'case2736sp' 'case2746wop' ...
        'case300' 'case30pwl' 'case39' 'case57' 'case9' ...
        'caseformat' 'case14' 'case24_ieee_rts' 'case2737sop' ...
        'case2746wp' 'case30' 'case30Q' 'case4gs' 'case6ww' ...
        'case9Q' 'case_ieee30'};

casenames = {'case300' 'case30pwl' 'case39' 'case57' 'case9' ...
        'case14' 'case24_ieee_rts' 'case30' 'case30Q' 'case4gs' 'case6ww' ...
        'case9Q' 'case_ieee30'};

%casenames = {'case4gs'};

root = '~/java/jacobi/JPOWER/matrix'

if (1)
  mkdirs(root, casenames);
end

for i=1:size(casenames, 2)
  cn = casenames{i};
  fprintf('Running: %s\n', cn);
  testcase(root, cn);
end



function testcase(root, casename)
%% test loadcase
mpc = loadcase(casename);
mmwrite_case(mpc, root, casename, 'loadcase');

%% test ext2int
mpc = ext2int(mpc);
mmwrite_case(mpc, root, casename, 'ext2int');

%% test bustypes
[ref, pv, pq] = bustypes(mpc.bus, mpc.gen);
mmwrite(strcat(root, '/', casename, '/bustypes/', 'ref.mtx'), ref, str2mat(strcat(casename,' ref bus indices')))
mmwrite(strcat(root, '/', casename, '/bustypes/', 'pv.mtx'), pv, str2mat(strcat(casename,' PV bus indices')))
mmwrite(strcat(root, '/', casename, '/bustypes/', 'pq.mtx'), pq, str2mat(strcat(casename,' PQ bus indices')))

%% test makeBdc
[Bbus, Bf, Pbusinj, Pfinj] = makeBdc(mpc.baseMVA, mpc.bus, mpc.branch);
mmwrite(strcat(root, '/', casename, '/makeBdc/', 'Bbus.mtx'), Bbus, str2mat(strcat(casename,' Bdc bus matrix')))
mmwrite(strcat(root, '/', casename, '/makeBdc/', 'Bf.mtx'), Bf, str2mat(strcat(casename,' Bdc from bus matrix')))
mmwrite(strcat(root, '/', casename, '/makeBdc/', 'Pbusinj.mtx'), Pbusinj, str2mat(strcat(casename,' Bdc bus phase shift injection vector')))
mmwrite(strcat(root, '/', casename, '/makeBdc/', 'Pfinj.mtx'), Pfinj, str2mat(strcat(casename,' Bdc from bus phase shift injection vector')))

%% test makeSbus
Sbus = makeSbus(mpc.baseMVA, mpc.bus, mpc.gen);
mmwrite(strcat(root, '/', casename, '/makeSbus/', 'Sbus.mtx'), Sbus, str2mat(strcat(casename,' Sbus')))

%% test dcpf
Va0 = mpc.bus(:, 9) * (pi/180);
Va = dcpf(Bbus, real(Sbus), Va0, ref, pv, pq);
mmwrite(strcat(root, '/', casename, '/dcpf/', 'Va.mtx'), Va, str2mat(strcat(casename,' Va')))

%% test int2ext
mpc = int2ext(mpc);
mmwrite_case(mpc, root, casename, 'int2ext');

%% test rundcpf
mpopt = mpoption('OUT_ALL', 0, 'VERBOSE', 0);
results = rundcpf(casename, mpopt);
mmwrite_case(results, root, casename, 'rundcpf');


function mmwrite_case(mpc, root, casename, fname)
mmwrite(strcat(root, '/', casename, '/', fname, '/', 'version.mtx'), str2num(mpc.version), str2mat(strcat(casename,' case format version')))
mmwrite(strcat(root, '/', casename, '/', fname, '/', 'baseMVA.mtx'), mpc.baseMVA, str2mat(strcat(casename,' system base')))
mmwrite(strcat(root, '/', casename, '/', fname, '/', 'bus.mtx'), mpc.bus, str2mat(strcat(casename,' bus data')))
mmwrite(strcat(root, '/', casename, '/', fname, '/', 'gen.mtx'), mpc.gen, str2mat(strcat(casename,' gen data')))
mmwrite(strcat(root, '/', casename, '/', fname, '/', 'branch.mtx'), mpc.branch, str2mat(strcat(casename,' branch data')))
if (isfield(mpc, 'areas'))
  mmwrite(strcat(root, '/', casename, '/', fname, '/', 'areas.mtx'), mpc.areas, str2mat(strcat(casename,' area data')))
end
if (isfield(mpc, 'gencost'))
  mmwrite(strcat(root, '/', casename, '/', fname, '/', 'gencost.mtx'), mpc.gencost, str2mat(strcat(casename,' gencost data')))
end


function mkdirs(root, casenames)
for i=1:size(casenames, 2)
  cn = casenames{i};
  mkdir(strcat(root, '/', cn), 'loadcase');
  mkdir(strcat(root, '/', cn), 'ext2int');
  mkdir(strcat(root, '/', cn), 'bustypes');
  mkdir(strcat(root, '/', cn), 'makeBdc');
  mkdir(strcat(root, '/', cn), 'makeSbus');
  mkdir(strcat(root, '/', cn), 'dcpf');
  mkdir(strcat(root, '/', cn), 'int2ext');
  mkdir(strcat(root, '/', cn), 'rundcpf');
end

