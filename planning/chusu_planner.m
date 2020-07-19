% MOPSO for chusu_bot
% @author glauberrleite

clear;
clc;

%% Getting World Info
grid = rand(30);
%grid = 0.1 .* ones(30);
[width, height] = size(grid);

% Add some high score cell for test
%grid(2,2) = 1;
%grid(2,3) = 1;
%grid(2,4) = 1;

%% Initialize swarm
n = 4;              % Robot carrying capacity
num_particles = 500;  % Swarm population

swarm.X = zeros(num_particles, n * 2);

swarm.X_self_obj = zeros(num_particles, 2);

% Fill populations based on grid dimensions
for i = 1:num_particles
    for j = 1:2:n*2
        % Random Numbers Within Specified Interval [1, width] and [1, height]
        swarm.X(i, j) = round(1 + (width - 1) * rand);
        swarm.X(i, j + 1) = round(1 + (height - 1) * rand);
    end
    
    [swarm.X_self_obj(i, 1), swarm.X_self_obj(i, 2)] = objectives(swarm.X(i,:), grid);
end

swarm.X_self = swarm.X;

swarm.V = zeros(num_particles, n * 2); % Particles start without velocity

%% Initialize External archive
size_archive = 5;

swarm.archive = zeros(size_archive, n * 2);
swarm.archive_obj = [zeros(size_archive, 1), Inf * ones(size_archive, 1)];

for i = 1:num_particles
    [swarm.archive, swarm.archive_obj] = addToArchive(swarm.X_self(i, :), swarm.X_self_obj(i, :), swarm.archive, swarm.archive_obj);
end

%% Iterations
num_iterations = 1000;
i = 0;

omega = 0.5;
rho_1 = 0.8;
rho_2 = 0.6;

while (i < num_iterations)
    for j = 1:num_particles
        
        % Select X_neigh, based on external archive
        index = round(1 + (size_archive - 1) * rand);
        X_neigh = swarm.archive(index, :);        
        
        % Compute new velocity
        swarm.V(j, :) = omega .* swarm.V(j, :) ...
            + rho_1 .* rand .* (swarm.X_self(j, :) - swarm.X(j, :)) ...
            + rho_2 .* rand .* (X_neigh - swarm.X(j, :));
        
        % Compute new position
        swarm.X(j, :) = swarm.X(j, :) + round(swarm.V(j, :));
        
        swarm.X(j, swarm.X(j, :) < 1) = 1;          % Constraints
        swarm.X(j, swarm.X(j, :) > width) = width;  % Constraints
        
        % Apply objective functions
        [H, D] = objectives(swarm.X(j, :), grid);
        
        % Update X_self
        if (dominates([H, D], swarm.X_self_obj(j, :)))
            swarm.X_self(j, :) = swarm.X(j, :);
            swarm.X_self_obj(j, :) = [H, D];
        end
        
        % Update external archive, if current solution is better than
        % anyone in archive
        [swarm.archive, swarm.archive_obj] = addToArchive(swarm.X(j, :), [H, D], swarm.archive, swarm.archive_obj);
        
    end
    
    i = i + 1;
end

%% Choose and show best trajectory
H = max(swarm.archive_obj(:, 1));
index_H = find(swarm.archive_obj(:, 1) == H);
[D, index_D] = min(swarm.archive_obj(index_H, 2));

best_particle = index_H(index_D);

disp('SCORE')
disp('----------------')
disp(['H = ', num2str(H), '; D = ', num2str(D)])
disp('----------------')


for i = 1:2:2*n
    disp(['Cell ', num2str(round(i/2))])
    disp('----------------')
    disp(['X = ', num2str(swarm.archive(best_particle, i)), '; Y = ', num2str(swarm.archive(best_particle, i+1))])
    disp('----------------')
end

