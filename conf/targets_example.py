def scriptIncludeFilter(result):
    return result.name == "ArrayUtil"

targets = [{'table' : 'sys_script_include',
            'nameField' : 'name',
            'contentField' : 'script',
            'localDir' : '/Users/username/documents/project',
            'query' : 'nameCONTAINSUtil',
            'recordFilter' : scriptIncludeFilter,
            'transformName' : lambda name : name[3:] + ".js"}
           ]
