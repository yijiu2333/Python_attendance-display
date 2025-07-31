import React, { useState, useEffect } from 'react';
import CardComponent from './components/CardComponent';
import TableComponent from './components/TableComponent';
import BarChartComponent from './components/BarChartComponent';
import * as XLSX from 'xlsx';
import './App.css';

import logo from './assets/logo.jpg'; // 导入logo图片
import kehu from './assets/kehu.png'; // 导入总人数图标
import zhuanshenren from './assets/zhuanshenren.png'; // 导入入职离职图标

function App() {
  // 状态管理
  const [state, setState] = useState({
    data: [],
    center_data: [],
    current_time: '',
    day_in: 0,
    day_out: 0,
    sum_number: 0,
    chart_data: [],
    male_number: 1000,
    female_number: 1500
  });

  // 定时更新数据
  useEffect(() => {
    const interval = setInterval(() => {
      updateData();
      updateTime();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // 更新时间
  const updateTime = () => {
    const currentTime = new Date().toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    setState(prev => ({...prev, current_time: `${currentTime} 部门及车间考勤数据看板`}));
  };

  // 更新数据
  const updateData = async () => {
    try {
      const response = await fetch('./assets/attendance.xlsx');
      const arrayBuffer = await response.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer);
      console.log('原始Excel数据:', workbook);
      
      // 获取工作表数据
      const worksheet = workbook.Sheets[workbook.SheetNames[0]];
      const hrWorksheet = workbook.Sheets[workbook.SheetNames[0]];
      
      // 转换为JSON格式
      const data = XLSX.utils.sheet_to_json(worksheet, {skipRows: [0,40,41,42], header: 1});
      const hrData = XLSX.utils.sheet_to_json(hrWorksheet, {header: 1});
      console.log('转换后的部门数据:', data);
      console.log('转换后的HR数据:', hrData);
      
      // 提取HR数据
      const hrRow = hrData[40];
      const sumNumber = hrRow ? parseInt(hrRow['__EMPTY_2']) : 0;
      const dayIn = hrRow ? parseInt(hrRow['__EMPTY']) : 0;
      const dayOut = hrRow ? parseInt(hrRow['__EMPTY_1']) : 0;
      
      // 处理部门数据
      const chartData = data.map(row => ({
        name: row['部门'],
        value: parseInt(row['应到人数'])
      }));
      
      // 筛选车间和部门数据
      const isWorkshop = (dept) => dept && dept.includes('车间');
      const workshopData = data
        .filter(row => isWorkshop(row['部门']))
        .sort((a, b) => b['出勤率'] - a['出勤率'])
        .map((row, i) => ({
          id: i,
          department: row['部门'],
          expected: parseInt(row['应到人数']),
          actual: parseInt(row['实到人数']),
          attendance_rate: Math.round(row['出勤率'] * 100),
          absentees: row['缺勤人员姓名及原因'] || '',
          remarks: row['备注'] || ''
        }));
      
      const deptData = data
        .filter(row => !isWorkshop(row['部门']))
        .sort((a, b) => b['出勤率'] - a['出勤率'])
        .map((row, i) => ({
          id: i,
          department: row['部门'],
          expected: parseInt(row['应到人数']),
          actual: parseInt(row['实到人数']),
          attendance_rate: Math.round(row['出勤率'] * 100),
          absentees: row['缺勤人员姓名及原因'] || '',
          remarks: row['备注'] || ''
        }));
      
      // 更新状态
      setState(prev => ({
        ...prev,
        data: deptData,
        center_data: workshopData,
        chart_data: chartData,
        sum_number: sumNumber,
        day_in: dayIn,
        day_out: dayOut
      }));
      
    } catch (error) {
      console.error('加载数据失败:', error);
      
      // 检查文件是否存在
      try {
        const fileCheck = await fetch('./assets/attendance.xlsx');
        if (!fileCheck.ok) {
          console.error('文件不存在或路径错误');
          return;
        }
        
        // 检查文件内容是否有效
        const buffer = await fileCheck.arrayBuffer();
        if (buffer.byteLength === 0) {
          console.error('文件内容为空或已损坏');
          return;
        }
        
        // 检查文件格式
        try {
          XLSX.read(buffer);
        } catch (e) {
          console.error('文件格式无效:', e.message);
          return;
        }
      } catch (fileError) {
        console.error('文件检查失败:', fileError);
      }
    }
  };

  return (
    <div className="app-container">
      {/* 顶部标题和时间 */}
      <div className="header">
        <img src={logo} alt="Logo" className="logo" />
        <h1 className="title">{state.current_time}</h1>
      </div>

      {/* 统计卡片 */}
      <div className="stats-container">
        {/* 总人数卡片 */}
        <CardComponent 
          title="总人数"
          value={state.sum_number}
          icon={kehu}
          altText="总人数"
          bgColor="#265589"
          shadowColor="rgba(10, 9, 60, 0.1)"
        />

        {/* 本日入职人数卡片 */}
        <CardComponent 
          title="本日入职人数"
          value={state.day_in}
          icon={zhuanshenren}
          altText="本日入职"
          bgColor="#8ea9c4"
          shadowColor="rgba(15, 83, 42, 0.1)"
        />

        {/* 本月离职人数卡片 */}
        <CardComponent 
          title="本月离职人数"
          value={state.day_out}
          icon={zhuanshenren}
          altText="本月离职"
          bgColor="#cbaea8"
          shadowColor="rgba(67, 11, 53, 0.1)"
        />
      </div>

      {/* 图表和表格部分 */}
      <div className="content-container">
        {/* 图表组件 */}
        <div style={{padding: '1rem', margin: 'auto'}}>
          <h3>各部门人数分布</h3>
          <BarChartComponent data={state.chart_data} />
        </div>

        {/* 表格组件 */}
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          {/* 车间表格 */}
          <TableComponent data={state.center_data} title="车间每日出勤" />

          {/* 部门表格 */}
          <TableComponent data={state.data} title="部门每日出勤" />
        </div>
      </div>
    </div>
  );
}

export default App;