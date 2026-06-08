#!/usr/bin/env python3
"""辅助函数用于绘制特殊形状"""

def draw_triangle(c, x, y, size, color, outline=False):
    """绘制三角形"""
    # 等腰三角形顶点
    points = [
        (x, y - size),  # 上顶点
        (x + size, y + size),  # 右下
        (x - size, y + size)   # 左下
    ]
    
    if outline:
        # 绘制轮廓
        for i in range(3):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % 3]
            c.line(x1, y1, x2, y2, color, 2)
    else:
        # 填充三角形（简化实现）
        # 找到最小和最大y坐标
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        for yy in range(int(min_y), int(max_y) + 1):
            # 找到与这条水平线相交的x坐标
            xs = []
            for i in range(3):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % 3]
                
                if (y1 <= yy <= y2) or (y2 <= yy <= y1):
                    if y1 != y2:
                        # 计算交点
                        t = (yy - y1) / (y2 - y1)
                        xs.append(x1 + t * (x2 - x1))
            
            if len(xs) >= 2:
                # 绘制水平线段
                x_start = min(xs)
                x_end = max(xs)
                for xx in range(int(x_start), int(x_end) + 1):
                    c.px(xx, yy, color)

def draw_diamond(c, x, y, size, color, outline=False):
    """绘制菱形"""
    # 菱形顶点
    points = [
        (x, y - size),  # 上
        (x + size, y),  # 右
        (x, y + size),  # 下
        (x - size, y)   # 左
    ]
    
    if outline:
        # 绘制轮廓
        for i in range(4):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % 4]
            c.line(x1, y1, x2, y2, color, 2)
    else:
        # 填充菱形（简化实现）
        # 分为上下两个三角形
        # 上三角形
        for yy in range(int(y - size), int(y) + 1):
            dy = yy - (y - size)
            width = size * (1 - dy / size)
            for xx in range(int(x - width), int(x + width) + 1):
                c.px(xx, yy, color)
        
        # 下三角形
        for yy in range(int(y), int(y + size) + 1):
            dy = yy - y
            width = size * (1 - dy / size)
            for xx in range(int(x - width), int(x + width) + 1):
                c.px(xx, yy, color)

def draw_rect_outline(c, x, y, w, h, color, thickness=2):
    """绘制矩形边框"""
    # 上边
    for xx in range(int(x), int(x + w) + 1):
        for t in range(thickness):
            c.px(xx, y + t, color)
    
    # 下边
    for xx in range(int(x), int(x + w) + 1):
        for t in range(thickness):
            c.px(xx, y + h - t - 1, color)
    
    # 左边
    for yy in range(int(y), int(y + h) + 1):
        for t in range(thickness):
            c.px(x + t, yy, color)
    
    # 右边
    for yy in range(int(y), int(y + h) + 1):
        for t in range(thickness):
            c.px(x + w - t - 1, yy, color)

def draw_dashed_line(c, x1, y1, x2, y2, color, thickness=2, dash=[5, 3]):
    """绘制虚线"""
    import math
    
    # 计算线段长度和角度
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
    
    # 单位向量
    ux = dx / length
    uy = dy / length
    
    dash_on, dash_off = dash
    dash_length = dash_on + dash_off
    
    current = 0
    while current < length:
        segment_end = min(current + dash_on, length)
        
        # 计算起点和终点
        sx = x1 + current * ux
        sy = y1 + current * uy
        ex = x1 + segment_end * ux
        ey = y1 + segment_end * uy
        
        # 绘制实线段
        c.line(sx, sy, ex, ey, color, thickness)
        
        current += dash_length