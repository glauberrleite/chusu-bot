% MOPSO for chusu_bot
% @author glauberrleite

clear;
clc;

%% Getting World Info
grid = rand(30);
[width, height] = size(grid);

%% Initialize swarm
n = 4;              % Robot carrying capacity
num_particles = 5;  % Swarm population

swarm.X = zeros(num_particles, n * 2);

swarm.X_self = swarm.X;
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

swarm.V = zeros(num_particles, n * 2); % Particles start without velocity

%% Initialize External archive
size_archive = 3;

swarm.archive = zeros(size_archive, n * 2);
swarm.archive_obj = zeros(size_archive, 2);

for i = 1:num_particles
    [swarm.archive, swarm.archive_obj] = addToArchive(swarm.X(i, :), swarm.archive, swarm.archive_obj);
end

%% Iterations
num_iterations = 10;
i = 0;

omega = 0.1;
rho_1 = 0.4;
rho_2 = 0.5;

while (i < num_iterations)
    for j = 1:num_particles
        
        % Select X_neigh, based on external archive
        X_neigh = swarm.X(j, :);
        for k = 1:size_archive
        end 
        
        % Compute new velocity
        swarm.V(j, :) = omega .* swarm.V(j, :) ...
            + rho_1 .* (swarm.X_self(j, :) - swarm.X(j, :)) ...
            + rho_2 .* (X_neigh - swarm.X(j, :));
        
        % Compute new position
        swarm.X(j, :) = swarm.X(j, :) + swarm.V(j, :);
            
        
        
    end
end