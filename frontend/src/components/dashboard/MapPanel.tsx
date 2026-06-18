"use client";

import { useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useFilter } from '@/hooks/useFilter';

// 模拟村组数据（当API不可用时）
const mockVillages = [
  { code: '370199001', name: '张家庄村', lat: 36.65, lng: 117.02 },
  { code: '370199002', name: '李家沟村', lat: 36.68, lng: 117.05 },
  { code: '370199003', name: '王家屯村', lat: 36.62, lng: 117.08 },
  { code: '370199004', name: '赵家湾村', lat: 36.70, lng: 117.10 },
  { code: '370199005', name: '刘家坡村', lat: 36.67, lng: 117.12 },
];

// 默认中心点（山东省济南市附近）
const DEFAULT_CENTER: [number, number] = [36.65, 117.05];
const DEFAULT_ZOOM = 11;

// 地图定位组件
function MapLocator({ center }: { center: [number, number] }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, map.getZoom(), { animate: true });
  }, [center, map]);
  
  return null;
}

interface MapPanelProps {
  className?: string;
  onVillageClick?: (code: string, name: string) => void;
}

export default function MapPanel({ className = '', onVillageClick }: MapPanelProps) {
  const { villageCode } = useFilter();
  
  // 计算地图中心点
  const mapCenter = useMemo(() => {
    if (villageCode) {
      const village = mockVillages.find(v => v.code === villageCode);
      if (village) {
        return [village.lat, village.lng] as [number, number];
      }
    }
    return DEFAULT_CENTER;
  }, [villageCode]);
  
  const mapZoom = villageCode ? 14 : DEFAULT_ZOOM;
  
  return (
    <div className={`relative flex-1 ${className}`}>
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ 
          height: '100%', 
          width: '100%',
          background: 'var(--bg-primary)',
        }}
        zoomControl={false}
      >
        {/* 使用 OpenStreetMap 作为底图（天地图降级方案） */}
        <TileLayer
          attribution=''
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* 深色地图样式覆盖层 */}
        <TileLayer
          attribution=''
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {/* 村组标记点 */}
        {mockVillages.map((village) => (
          <Marker
            key={village.code}
            position={[village.lat, village.lng]}
          >
            <Popup>
              <div 
                style={{ color: '#e8f0ff', fontSize: '12px' }}
                onClick={() => {
                  if (onVillageClick) {
                    onVillageClick(village.code, village.name);
                  }
                }}
              >
                <strong style={{ color: '#00d4ff', cursor: 'pointer' }}>{village.name}</strong>
                <br />
                <span style={{ color: 'rgba(180,200,240,0.75)' }}>编码: {village.code}</span>
                <br />
                <span 
                  style={{ 
                    color: '#00d4ff', 
                    fontSize: '11px',
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  点击查看详情
                </span>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* 地图定位 */}
        <MapLocator center={mapCenter} />
      </MapContainer>
      
      {/* 底部版权信息 */}
      <div 
        className="absolute bottom-[4px] left-[4px] text-[10px] z-[1000]"
        style={{ color: 'var(--text-muted)' }}
      >
        天地图 GS(2024)0568号 | OpenStreetMap contributors
      </div>
    </div>
  );
}