USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_DataSizeGrowth_S]    Script Date: 2022-02-11 ¿ÀÀü 9:29:46 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_DataSizeGrowth_S](
	[CollectDate] [datetime] NOT NULL,
	[InstanceID] [int] NOT NULL,
	[Database_id] [int] NOT NULL,
	[DatabaseName] [varchar](200) NULL,
	[TotalSizeMB] [decimal](38, 2) NULL,
	[UsedSizeMB] [decimal](38, 2) NULL,
 CONSTRAINT [PK_TB_DataSizeGrowth_S] PRIMARY KEY CLUSTERED 
(
	[CollectDate] ASC,
	[InstanceID] ASC,
	[Database_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


