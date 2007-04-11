% generate plots for VF10-5 bandwidth studies
% Mark 01/25/05

pulse = load('vf105.pul');
spectrum = load('vf105.spec');

% center the time axis for the pulse plot
TimePulse = pulse(:,1)*1e6; % us
[M,I]=max(pulse(:,2));
TimePulse = TimePulse - pulse(I,1)*1e6;
Pulse = pulse(:,2)./max(pulse(:,2));

figure;
subplot(2,1,1);
plot(TimePulse,Pulse);
xlabel('Time (us)');
title('VF10-5 Impulse Response');
axis([-0.5 0.5 -1.1 1.1]);

subplot(2,1,2);
plot(spectrum(:,1)/1e6,spectrum(:,2));
xlabel('Frequency (MHz)');
title('VF10-5 Frequency Spectrum');
text(6.0,-85,'-6 dB BW: 5.24 - 9.89 MHz');
text(6.0,-90,'Fractional Bandwidth = 66%');
axis([2 13 -100 -60]);

print -dpng VF105plots.png
