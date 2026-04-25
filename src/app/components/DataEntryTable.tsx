import { useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { LineChart, Table2, FileSpreadsheet, PieChart } from "lucide-react";
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from "recharts";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Label } from "./ui/label";

interface DataRecord {
  id: string;
  sampleName: string;
  temperature: string;
  weight: string;
  length: string;
  width: string;
  height: string;
  waterCutWidth: string;
  timestamp: string;
}

interface SensorData {
  temperature: number;
  weight: number;
  timestamp: Date;
}

interface DataEntryTableProps {
  isWaterCutEnabled: boolean;
  sampleType: string;
  sampleName: string;
  currentSensorData: SensorData;
  onAddRecord?: (record: DataRecord) => void;
  weightRange?: { min: number; max: number };
}

export function DataEntryTable({
  isWaterCutEnabled,
  sampleType,
  sampleName,
  currentSensorData,
  onAddRecord,
  weightRange,
}: DataEntryTableProps) {
  const [records, setRecords] = useState<DataRecord[]>([
    {
      id: "1",
      sampleName: "样品-001",
      temperature: "25.3",
      weight: "125.45",
      length: "100.5",
      width: "50.2",
      height: "30.1",
      waterCutWidth: "45.8",
      timestamp: new Date().toLocaleString("zh-CN"),
    },
    {
      id: "2",
      sampleName: "样品-002",
      temperature: "26.1",
      weight: "132.20",
      length: "102.3",
      width: "51.1",
      height: "31.5",
      waterCutWidth: "46.2",
      timestamp: new Date(Date.now() - 60000).toLocaleString("zh-CN"),
    },
    {
      id: "3",
      sampleName: "样品-003",
      temperature: "24.8",
      weight: "118.90",
      length: "98.7",
      width: "49.5",
      height: "29.8",
      waterCutWidth: "44.9",
      timestamp: new Date(Date.now() - 120000).toLocaleString("zh-CN"),
    },
  ]);

  const [viewMode, setViewMode] = useState<"table" | "chart" | "pie">("table");
  const [chartMetric, setChartMetric] = useState<string>("weight");

  const metricOptions = [
    { value: "temperature", label: "温度 (°C)" },
    { value: "weight", label: "重量 (g)" },
    { value: "length", label: "长 (mm)" },
    { value: "width", label: "宽 (mm)" },
    { value: "height", label: "高 (mm)" },
    { value: "waterCutWidth", label: "水切宽度 (mm)" },
  ];

  // 准备图表数据
  const chartData = records.map((record) => ({
    time: record.timestamp,
    温度: parseFloat(record.temperature),
    重量: parseFloat(record.weight),
    长: parseFloat(record.length),
    宽: parseFloat(record.width),
    高: parseFloat(record.height),
    水切宽度: parseFloat(record.waterCutWidth),
  })).reverse();

  const getMetricKey = (metric: string) => {
    const map: Record<string, string> = {
      temperature: "温度",
      weight: "重量",
      length: "长",
      width: "宽",
      height: "高",
      waterCutWidth: "水切宽度",
    };
    return map[metric] || "重量";
  };

  const getMetricLabel = (metric: string) => {
    const option = metricOptions.find(opt => opt.value === metric);
    return option?.label || "重量 (g)";
  };

  const handleExportExcel = () => {
    console.log("导出为Excel格式");
    alert("Excel导出功能需要安装相关库（如 xlsx）");
  };

  // 计算重量占比数据
  const calculateWeightDistribution = () => {
    if (!weightRange || records.length === 0) {
      return [];
    }

    const { min, max } = weightRange;
    const average = (min + max) / 2;

    const categories = {
      above: 0,
      upperMid: 0,
      lowerMid: 0,
      below: 0,
    };

    records.forEach((record) => {
      const weight = parseFloat(record.weight);
      if (weight > max) {
        categories.above++;
      } else if (weight > average) {
        categories.upperMid++;
      } else if (weight > min) {
        categories.lowerMid++;
      } else {
        categories.below++;
      }
    });

    return [
      { name: `大于上限 (>${max}g)`, value: categories.above, color: "#ef4444" },
      { name: `上限-平均 (${average.toFixed(1)}-${max}g)`, value: categories.upperMid, color: "#f59e0b" },
      { name: `平均-下限 (${min}-${average.toFixed(1)}g)`, value: categories.lowerMid, color: "#10b981" },
      { name: `小于下限 (<${min}g)`, value: categories.below, color: "#3b82f6" },
    ].filter(item => item.value > 0);
  };

  const pieData = calculateWeightDistribution();

  return (
    <Card className="h-full bg-white border-gray-200 flex flex-col shadow-sm">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">数据录入</h3>
        <div className="flex items-center gap-2">
          {viewMode === "chart" && (
            <div className="flex items-center gap-2">
              <Label className="text-sm text-gray-700">指标选择:</Label>
              <Select value={chartMetric} onValueChange={setChartMetric}>
                <SelectTrigger className="w-40 bg-white border-gray-300">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {metricOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          {viewMode === "table" && (
            <Button size="sm" variant="outline" onClick={handleExportExcel}>
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              导出Excel
            </Button>
          )}
          <Button
            size="sm"
            variant={viewMode === "pie" ? "default" : "outline"}
            onClick={() => setViewMode(viewMode === "pie" ? "table" : "pie")}
          >
            <PieChart className="w-4 h-4 mr-2" />
            占比图
          </Button>
          <Button
            size="sm"
            variant={viewMode === "chart" ? "default" : "outline"}
            onClick={() => setViewMode(viewMode === "chart" ? "table" : "chart")}
          >
            {viewMode === "chart" ? (
              <>
                <Table2 className="w-4 h-4 mr-2" />
                表格
              </>
            ) : (
              <>
                <LineChart className="w-4 h-4 mr-2" />
                趋势图
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {viewMode === "table" ? (
          <Table>
            <TableHeader>
              <TableRow className="border-gray-200 hover:bg-gray-50">
                <TableHead className="text-gray-700">样品名称</TableHead>
                <TableHead className="text-gray-700">温度 (°C)</TableHead>
                <TableHead className="text-gray-700">重量 (g)</TableHead>
                <TableHead className="text-gray-700">长 (mm)</TableHead>
                <TableHead className="text-gray-700">宽 (mm)</TableHead>
                <TableHead className="text-gray-700">高 (mm)</TableHead>
                <TableHead className="text-gray-700">水切宽度 (mm)</TableHead>
                <TableHead className="text-gray-700">时间</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((record) => (
                <TableRow key={record.id} className="border-gray-200 hover:bg-gray-50">
                  <TableCell className="text-gray-700">{sampleName}</TableCell>
                  <TableCell className="text-gray-700">{record.temperature}</TableCell>
                  <TableCell className="text-gray-700">{record.weight}</TableCell>
                  <TableCell className="text-gray-700">{record.length}</TableCell>
                  <TableCell className="text-gray-700">{record.width}</TableCell>
                  <TableCell className="text-gray-700">{record.height}</TableCell>
                  <TableCell className="text-gray-700">
                    {isWaterCutEnabled ? record.waterCutWidth : "-"}
                  </TableCell>
                  <TableCell className="text-gray-500 text-sm">
                    {record.timestamp}
                  </TableCell>
                </TableRow>
              ))}

              {records.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-gray-500 py-8">
                    暂无数据记录
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        ) : viewMode === "chart" ? (
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <RechartsLineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="time" 
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                />
                <YAxis 
                  stroke="#6b7280"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  label={{ value: getMetricLabel(chartMetric), angle: -90, position: 'insideLeft', fill: '#374151' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#ffffff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey={getMetricKey(chartMetric)} 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="p-6">
            <h4 className="text-center text-gray-900 font-medium mb-4">重量分布占比图</h4>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={350}>
                <RechartsPieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#ffffff', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px'
                    }}
                  />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                暂无数据或未配置重量范围
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}