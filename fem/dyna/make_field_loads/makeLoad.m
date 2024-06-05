function makeLoad(ii)

    % Project Root
    projectRoot = pwd;

    % Get home folder (windows and linux)
    if ispc
        homeFolder = getenv('USERPROFILE');
    else
        homeFolder = getenv('HOME');
    end

    % Add Field II to path
    addpath(genpath(fullfile(homeFolder, 'repos', 'field2')));

    % Add transducer definitions to path
    addpath(genpath(fullfile(homeFolder, 'repos', 'transducers')));

    focal_depth_arr = 10:1:40;
    fnum_arr = [1.5, 3.0, 5.0];
    alpha_arr = 0.1:0.1:1.5;
    % transducer_arr = [1, 2];
    params = cartesian(focal_depth_arr, fnum_arr, alpha_arr);

    nparams = size(params, 1);

    % for ii = 1:nparams
    fprintf('Simulation [%d/%d]\n', ii, nparams);

    fd = params(ii, 1);
    fnum = params(ii, 2);
    alpha = params(ii, 3);
    % txer = params(ii, 4);

    FIELD_PARAMS.Frequency = 4.21;
    FIELD_PARAMS.Transducer = 'L74';
    % if txer == 1
    %     FIELD_PARAMS.Frequency = 4.21;
    %     FIELD_PARAMS.Transducer = 'vf73';
    % else
    %     FIELD_PARAMS.Frequency = 4.0;

    %     if fd < 25
    %         FIELD_PARAMS.Transducer = 'l94_row1';
    %     else
    %         FIELD_PARAMS.Transducer = 'l94_row3';
    %     end

    % end

    FIELD_PARAMS.focus = [0, 0, fd * 1e-3];
    FIELD_PARAMS.Fnum = fnum;
    FIELD_PARAMS.alpha = alpha;
    ncyc = 70;

    FIELD_PARAMS.soundSpeed = 1540;
    FIELD_PARAMS.samplingFrequency = 200e6;
    FIELD_PARAMS.Impulse = 'gaussian';

    fd = int16(FIELD_PARAMS.focus * 1e3);
    txer_folder_name = sprintf('txer=%s', FIELD_PARAMS.Transducer);
    filename = sprintf('fd=[%d,%d,%d]&fnum=%.1f&att=%.1f.mat', fd(1), fd(2), fd(3), fnum, alpha);
    load_file = fullfile('loads', txer_folder_name, filename);

    if ~isfile(load_file)

        wavelength = FIELD_PARAMS.soundSpeed / (FIELD_PARAMS.Frequency * 1e6);

        extent.ele = [-0.005, 0.005];
        extent.lat = [-0.005, 0.005];
        extent.ax = [-0.005, -0.05];

        nele = floor((extent.ele(2) - extent.ele(1)) / wavelength);
        nlat = floor((extent.lat(2) - extent.lat(1)) / wavelength);
        nax = -1 * floor((extent.ax(2) - extent.ax(1)) / wavelength);

        scale = 2;
        nele = floor(scale * nele) + 1;
        nlat = floor(scale * nlat) + 1;
        nax = floor(scale * nax) + 1;

        coords.ele = linspace(extent.ele(1), extent.ele(2), nele);
        coords.lat = linspace(extent.lat(1), extent.lat(2), nlat);
        coords.ax = linspace(extent.ax(1), extent.ax(2), nax);

        mp = cartesian(coords.ax, coords.lat, coords.ele);
        mp(:, [1, 2, 3]) = mp(:, [2, 3, 1]);
        mp(:, 3) = -1 * mp(:, 3);

        FIELD_PARAMS.measurementPoints = mp;

        %
        field_init(-1)

        disp('Starting the Field II simulation');

        % define transducer-independent parameters
        set_field('c', FIELD_PARAMS.soundSpeed);
        set_field('fs', FIELD_PARAMS.samplingFrequency);

        % define transducer-dependent parameters
        eval(sprintf('[Th,impulseResponse]=%s(FIELD_PARAMS);', FIELD_PARAMS.Transducer));

        % define the impulse response
        xdc_impulse(Th, impulseResponse);

        % define the excitation pulse
        exciteFreq = FIELD_PARAMS.Frequency * 1e6; % Hz
        texcite = 0:1 / FIELD_PARAMS.samplingFrequency:ncyc / exciteFreq;
        excitationPulse = sin(2 * pi * exciteFreq * texcite);
        xdc_excitation(Th, excitationPulse);

        % set attenuation
        Freq_att = FIELD_PARAMS.alpha * 100/1e6; % FIELD_PARAMS in dB/cm/MHz
        att_f0 = exciteFreq;
        att = Freq_att * att_f0; % set non freq. dep. to be centered here
        set_field('att', att);
        set_field('freq_att', Freq_att);
        set_field('att_f0', att_f0);
        set_field('use_att', 1);

        % compute Ispta at each location for a single tx pulse
        % optimizing by computing only relevant nodes... will assume others are zero
        StartTime = fix(clock);
        fprintf('Start Time: %i:%i\n', StartTime(4), StartTime(5));
        tic;
        EstCount = 1000; % number of calculations to average over to
        % make calc time estimates
        numNodes = size(FIELD_PARAMS.measurementPoints, 1);
        progressPoints = 0:10000:numNodes;
        intensity = [];

        for i = 1:numNodes

            if ~isempty(intersect(i, progressPoints))
                fprintf('Processed %.1f%%\n', i * 100 / numNodes);
            end

            [pressure, startTime] = calc_hp(Th, FIELD_PARAMS.measurementPoints(i, :));
            intensity(i) = sum(pressure .* pressure);

            if (i == 1)
                tic
            end

        end

        CalcTime = toc; % s
        ActualRunTime = CalcTime / 60; % min
        fprintf('Actual Run Time = %.1f m\n\n', ActualRunTime);

        field_end;

        save(load_file, 'intensity', 'FIELD_PARAMS');

    end

end
