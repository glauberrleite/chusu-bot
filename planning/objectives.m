function [H, D] = objectives(X, grid)
    H = 0;
    D = 0;
    
    % Check if there are duplicates in X
    for i = 1:2:length(X)
        for j = 1:2:length(X)
            if (i ~= j)
                if (X(i) == X(j)) && (X(i+1) == X(j+1))
                    D = Inf;
                    return; % Stops function execution
                end
            end
        end
    end
    
    % Apply objective functions
    for i = 1:2:length(X)
        H = H + grid(X(i), X(i + 1));

        if (i < length(X) - 2)
            D = D + sqrt((X(i) - X(i+2))^2 + ((X(i+1) - X(i+3))^2));
        end
    end
end