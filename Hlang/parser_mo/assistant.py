def filter_anno_blankrow(source):
    # 非常不优雅的解决方法
    new_source = [line for line in source.split("\n") if line.strip() and not line.startswith("#")]
    return "\n".join(new_source)