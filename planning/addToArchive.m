function [newArchive, new_obj] = addToArchive(candidate, obj, archive, archive_obj)

    for i = 1:size(archive, 1)
        if (dominates(obj, archive_obj(i, :)))
            % Updates archive
            archive(i, :) = candidate;
            archive_obj(i, :) = obj;
            break
        end
    end
    
    newArchive = archive;
    new_obj = archive_obj;
end