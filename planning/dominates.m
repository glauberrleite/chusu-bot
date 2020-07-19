function result = dominates(obj1, obj2)
    % Is obj1 better than obj2?
    % H = obj(1)
    % D = obj(2)
    if (obj1(1) >= obj2(1)) && (obj1(2) <= obj2(2)) % Not worst in all objectives
        if (obj1(1) > obj2(1)) || (obj1(2) < obj2(2)) % Strictly better in at least one objective
            result = true;
        else % The two result are equally good. Using random choice
            if (rand > 0.5)
                result = true;
            else
                result = false;
            end
        end
    else
        result = false;
    end
     
end